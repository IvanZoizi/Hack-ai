from .models import Photo
from .forms import PhotoForm
from django.shortcuts import render
from django.core.files.base import ContentFile
from .model import get_model

import cv2


def add_location(request):
    if request.method == 'GET':
        form = PhotoForm()
        #model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt')
        #model.classes = [0]
        #model.conf = 0.3
        #print(model([img2]).xyxy)
        #img = cv2.imread('images/4.JPG_0_0.jpg')
        #img2 = img[0:640, 0:640]
        #pred = model(img)
        return render(request, 'image.html', {'form': form})
    elif request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            for f in request.FILES.getlist('photos'):
                data = f.read()
                photo = Photo()
                photo.image.save(f.name, ContentFile(data))
                photo.save()
                SIDE = 640
                img = cv2.imread(photo.image.url[1:])
                h, w, _ = img.shape
                for x in range(0, w, SIDE):
                    for y in range(0, h, SIDE):
                        x_dif = 0
                        y_dif = 0
                        if x + SIDE > w:
                            x_dif = x + SIDE - w
                        if y + SIDE > h:
                            y_dif = y + SIDE - h
                        pred = get_model(img[y - y_dif:y + SIDE, x - x_dif:x + SIDE])
                        print(pred)
            return render(request, 'image.html', {'form': form})
        else:
            return render(request, 'image.html', {'form': form})