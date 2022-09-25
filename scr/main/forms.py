from django import forms


class PhotoForm(forms.Form):
    photos = forms.ImageField(label=u'Загрузите или переместите снимки для сканирования',
                              widget=forms.FileInput(attrs={"class": "menu_form", 'multiple': 'multiple'}), disabled=False,
                              )
