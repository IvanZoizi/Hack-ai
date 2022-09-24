from django import forms


class PhotoForm(forms.Form):
    photos = forms.ImageField(label=u'Фотографии', widget=forms.FileInput(attrs={'multiple': 'multiple'}))
    gpu_or_cpu = forms.BooleanField(label='Использовать GPU (В другом случае мы будем использовать CPU)', required=False)