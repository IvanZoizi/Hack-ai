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