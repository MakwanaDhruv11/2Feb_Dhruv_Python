from django.shortcuts import render
from django.http import JsonResponse
from .models import AboutInfo, Skill, Project, Experience, SocialLink, ContactMessage

def index(request):
    about = AboutInfo.objects.first()
    skills = Skill.objects.all()
    projects = Project.objects.all()
    experiences = Experience.objects.all().order_by('-id')
    socials = SocialLink.objects.all()
    
    context = {
        'about': about,
        'skills': skills,
        'projects': projects,
        'experiences': experiences,
        'socials': socials,
    }
    return render(request, 'portfolio/index.html', context)

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        if name and email and message:
            ContactMessage.objects.create(name=name, email=email, message=message)
            return JsonResponse({'status': 'success', 'message': 'Message sent successfully!'})
        else:
            return JsonResponse({'status': 'error', 'message': 'All fields are required.'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
