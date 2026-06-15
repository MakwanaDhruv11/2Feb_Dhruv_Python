from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile_list, name='profile_list'),
    path('create/', views.create_profile, name='create_profile'),
    path('export/', views.export_profiles, name='export_profiles'),
]
