import torch
import torchvision
import pandas
import requests
import yaml
import tqdm
import seaborn
import cv2

model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt')
model.classes = [0]
model.conf = 0.3


def get_model(image):
    model.eval()
    with torch.no_grad():
        pred = model(image)
    return pred


def gpu_cpu(flag):
    if flag:
        if torch.cuda.is_available():
            device = torch.device('cuda')

            print(f"Количество GPU {torch.cuda.device_count}")

            print(f"Используется {torch.cuda.get_device_name(0)}")
        else:
            device = torch.device('cpu')
    else:
        print('Нет доступных GPU')
        device = torch.device('cpu')
    model.to(device)