from django.urls import path
from .views import ResumeListView, ResumeUploadView, ResumeDetailView, ResumeDeleteView

app_name = 'resumes'

urlpatterns = [
    path('', ResumeListView.as_view(), name='resume_list'),
    path('upload/', ResumeUploadView.as_view(), name='resume_upload'),
    path('<int:pk>/', ResumeDetailView.as_view(), name='resume_detail'),
    path('<int:pk>/delete/', ResumeDeleteView.as_view(), name='resume_delete'),
]
