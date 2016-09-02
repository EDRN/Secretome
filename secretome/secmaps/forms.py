from django import forms

from .models import Hguids

class HguidForm(forms.ModelForm):

    class Meta:
        model = Hguids
        fields = ('hguid',)

class Hguid2Form(forms.ModelForm):

    class Meta:
        model = Hguids
        fields = ('hguid',)

class NameForm(forms.Form):
	your_name = forms.CharField(label='Your name', max_length=80)

class PostForm(forms.Form):
    content = forms.CharField(max_length=256)
    created_at = forms.DateTimeField()

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()
