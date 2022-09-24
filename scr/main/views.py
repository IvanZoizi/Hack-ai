from django.http import HttpResponseRedirect

from .models import Photo
from .forms import PhotoForm
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from .model import get_model
import zipfile

import cv2


def add_location(request):
    if request.method == 'GET':
        form = PhotoForm()
        return render(request, 'image.html', {'form': form})
    elif request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            image_list = []
            file = zipfile.ZipFile('media/photos/' + str(request.FILES.getlist('photos')[0]) + '.zip', 'w')
            print(1)
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
                image_list.append(f"{photo.image.url}")
                file.write(rf"{photo.image.url[1:]}")
            file.close()
            return render(request, 'save.html', {'images': image_list[1:], 'img1': image_list[0],
                                                 'name': str(request.FILES.getlist('photos')[0]) + '.zip'})
        elif request.POST.get("save_next"):
            form = PhotoForm()
            return render(request, 'image.html', {'form': form})
        else:
            form = PhotoForm()
            return render(request, 'image.html', {'form': form})