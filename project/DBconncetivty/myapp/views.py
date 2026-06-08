from django.shortcuts import render,redirect
from .forms import *

# Create your views here.

def index(request):
    if request.method == "POST":
        form = Studenstinfoform(request.POST)
        if form.is_valid():
            form.save()
            print('Data Inserted')
        else:
            print(form.error)
    return render(request, 'index.html')

def showdata(request):
    data = Studentinfo.objects.all()
    return render(request, 'showdata.html', {'data': data})

def deletedata(request,id):
    stid=Studentinfo.objects.get(id=id)
    Studentinfo.delete(stid)
    return redirect('showdata')
 