from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import UserProfile
from .forms import UserProfileForm
import csv
import os

def profile_list(request):
    profiles = UserProfile.objects.all()
    return render(request, 'profiles/profile_list.html', {'profiles': profiles})

def create_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('profile_list')
    else:
        form = UserProfileForm()
    return render(request, 'profiles/create_profile.html', {'form': form})

def export_profiles(request):
    profiles = UserProfile.objects.all()
    
    # Using Context Manager (with open(...) as file:) as requested
    filename = 'profiles_export.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Username', 'Age', 'Is Public'])
        for profile in profiles:
            writer.writerow([profile.username, profile.age, profile.is_public])
            
    # Read the file and prepare response
    with open(filename, 'rb') as file:
        response = HttpResponse(file.read(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
    # Clean up the temporary file
    if os.path.exists(filename):
        os.remove(filename)
        
    return response
