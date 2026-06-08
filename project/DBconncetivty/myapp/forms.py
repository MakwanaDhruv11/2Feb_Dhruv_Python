from django import forms
from .models import *

class Studenstinfoform(forms.ModelForm):
    class Meta:
        model = Studentinfo
        fields = '__all__'