from django.urls import path
from .views import JobListView, JobDetailView, JobFetchView

app_name = 'jobs'

urlpatterns = [
    path('', JobListView.as_view(), name='job_list'),
    path('<int:pk>/', JobDetailView.as_view(), name='job_detail'),
    path('fetch/', JobFetchView.as_view(), name='job_fetch'),
]
