from django.shortcuts import render
from django.shortcuts import render
from .models import Location, Photo
from .forms import FormImage, LocationForm
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile

import matplotlib.pyplot as plt
import cv2
from PIL import Image


def add_location(request):
    if request.method == 'GET':
        form = LocationForm()
        return render(request, 'image.html', {'form': form})
    elif request.method == 'POST':
        form = LocationForm(request.POST, request.FILES)
        if form.is_valid():
            location = Location.objects.create(name=form.cleaned_data['name'])
            for f in request.FILES.getlist('photos'):
                data = f.read()
                photo = Photo(location=location)
                photo.image.save(f.name, ContentFile(data))
                photo.save()
                SIDE = 500
                plt.subplots(6, 9, figsize=(25, 20))
                print(photo.image.url)
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
                        cv2.imwrite(f'images/savedImage{x}_{y}.jpg', img[y - y_dif:y + SIDE, x - x_dif:x + SIDE])
            return render(request, 'image.html', {'form': form, 'image': photo})
        else:
            return render(request, 'image.html', {'form': form})


def get_image(request):
    form = FormImage()
    if request.method == 'POST':
        form = FormImage(request.POST, request.FILES)
        for i in list(request.FILES.getlist('image')):
            print(1)
            print(i)
        if form.is_valid:
            form.save()

            image = form.instance

            print(image)

            return render(request, 'image.html', {'form': form, 'image': image})
    else:
        return render(request, 'image.html', {'form': form, 'image': 'бааубфацвабф'})