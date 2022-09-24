from django.db import models


class Photo(models.Model):
    image = models.ImageField(upload_to='photos')