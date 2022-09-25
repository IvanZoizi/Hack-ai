import torch
import torchvision
import pandas
import requests
import yaml
import tqdm
import seaborn
import cv2
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
import matplotlib.pyplot as plt
from PIL import Image
import os

class double_conv(nn.Module):
    """(conv => BN => ReLU) * 2"""

    def __init__(self, in_ch, out_ch):
        super(double_conv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        x = self.conv(x)
        return x


class inconv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super(inconv, self).__init__()
        self.conv = double_conv(in_ch, out_ch)

    def forward(self, x):
        x = self.conv(x)
        return x


class down(nn.Module):
    def __init__(self, in_ch, out_ch):
        super(down, self).__init__()
        self.mpconv = nn.Sequential(nn.MaxPool2d(2), double_conv(in_ch, out_ch))

    def forward(self, x):
        x = self.mpconv(x)
        return x


class up(nn.Module):
    def __init__(self, in_ch, out_ch, bilinear=True):
        super(up, self).__init__()

        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True)
        else:
            self.up = nn.ConvTranspose2d(in_ch // 2, in_ch // 2, 2, stride=2)

        self.conv = double_conv(in_ch, out_ch)

    def forward(self, x1, x2):
        x1 = self.up(x1)

        # input is CHW
        diffY = x2.size()[2] - x1.size()[2]
        diffX = x2.size()[3] - x1.size()[3]

        x1 = nn.functional.pad(x1, (diffX // 2, diffX - diffX // 2, diffY // 2, diffY - diffY // 2))

        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)


class outconv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super(outconv, self).__init__()
        self.conv = nn.Conv2d(in_ch, out_ch, 1)

    def forward(self, x):
        x = self.conv(x)
        return x


class UNet(nn.Module):
    def __init__(self, n_channels, n_classes):
        super(UNet, self).__init__()
        self.inc = inconv(n_channels, 64)
        self.down1 = down(64, 128)
        self.down2 = down(128, 256)
        self.down3 = down(256, 512)
        self.down4 = down(512, 512)
        self.up1 = up(1024, 256, False)
        self.up2 = up(512, 128, False)
        self.up3 = up(256, 64, False)
        self.up4 = up(128, 64, False)
        self.outc = outconv(64, n_classes)

    def forward(self, x):
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)
        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)
        x = self.outc(x)
        return torch.sigmoid(x)


model = UNet(n_channels=3, n_classes=1).float()

model.load_state_dict(torch.load('model_cifar.pt', map_location=torch.device('cpu')))

train_on_gpu = False


class CloudDataset(Dataset):
    def __init__(self, img_ids, datatype: str = 'train',
                 transforms=transforms.Compose([
                     transforms.ToPILImage(),
                     transforms.Resize((256, 256)),
                     transforms.ToTensor()]),
                 preprocessing=None):

        self.img_ids = img_ids
        self.transforms = transforms
        self.preprocessing = preprocessing

    #         print(self.img_ids)F

    def __getitem__(self, idx):
        #         image_name = self.img_ids[idx]
        #         mask = make_mask(self.df, image_name)
        #         image_path = os.path.join(self.data_folder, image_name)
        #         print(idx)
        #         print(f'main_test/savedImage{idx}.jpg')
        img = cv2.imread(f'main_test/savedImage{idx}.jpg')
        #         print(len(img))
        try:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        except:
            raise IndexError
        img = self.transforms(img)

        return img

    def __len__(self):
        #         print(self.img_ids)
        return len(self.img_ids)


def eval(image):
    img = cv2.imread(image)

    SIDE = 256
    h, w, _ = img.shape
    count = -1
    print(h, w)
    for x in range(0, w, SIDE):
        for y in range(0, h, SIDE):
            count += 1
            x_dif = 0
            y_dif = 0
            if x + SIDE > w:
                x_dif = x + SIDE - w
            if y + SIDE > h:
                y_dif = y + SIDE - h
            #         print(x, y)
            #         img[y - y_dif:y+SIDE, x - x_dif:x+SIDE]
            cv2.imwrite(f'main_test/savedImage{count}.jpg', img[y - y_dif:y + SIDE, x - x_dif:x + SIDE])

    num_workers = 0
    bs = 1
    train_dataset = CloudDataset(datatype='train', img_ids=[i for i in range(0, count)])
    train_loader = DataLoader(train_dataset, batch_size=bs, shuffle=False, num_workers=num_workers)
    print(train_loader)

    max_out = 0
    x_dif = 0
    y_dif = 0
    image = Image.new('RGB', (w, h), (250, 250, 250))
    for i, data in enumerate(train_loader):
        #print(i)
        if train_on_gpu:
            data = data.cuda()
        output = ((model(data))[0]).cpu().detach().numpy().reshape((256, 256, 1))
        print(i)
        max_out = output.sum()
        max_out_i = i
        max_output = output
        cv2.imwrite(f'result_test/{i}.jpg', output)
        img = Image.open(f'result_test/{i}.jpg')
        image.paste(img, (x_dif, y_dif))
        x_dif += SIDE
        if x_dif > w:
            y_dif += SIDE
            x_dif = 0
        if i == 578:
            print("Ecnm")
            print(x_dif, y_dif)
            image.paste(img, (x_dif, y_dif))
        os.remove(f'result_test/{i}.jpg')
    image.save(f"media/photos/{i}.jpg")
    return f"media/photos/{i}.jpg"


def gpu_cpu(flag):
    if flag:
        if torch.cuda.is_available():
            device = torch.device('cuda')

            print(f"Количество GPU {torch.cuda.device_count}")

            print(f"Используется {torch.cuda.get_device_name(0)}")
        else:
            device = torch.device('cpu')
        model.to(device)
    else:
        print('Нет доступных GPU')
        device = torch.device('cpu')
