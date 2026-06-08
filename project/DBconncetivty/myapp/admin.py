from django.contrib import admin
from .models import *

# Register your models here.
class stdata(admin.ModelAdmin):
    list_display = ['name','email','dob','mobile','address']

admin.site.register(Studentinfo,stdata)