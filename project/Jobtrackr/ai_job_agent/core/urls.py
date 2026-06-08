from django.urls import path
from .views import (
    IndexView, DashboardView, MatchedJobsListView, 
    SavedJobsListView, AppliedJobsListView, SettingsView,
    SaveJobActionView, ApplyJobActionView
)

app_name = 'core'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/matches/', MatchedJobsListView.as_view(), name='matched_jobs'),
    path('dashboard/saved/', SavedJobsListView.as_view(), name='saved_jobs'),
    path('dashboard/applied/', AppliedJobsListView.as_view(), name='applied_jobs'),
    path('dashboard/settings/', SettingsView.as_view(), name='settings'),
    
    # Action triggers
    path('jobs/<int:pk>/save/', SaveJobActionView.as_view(), name='save_job'),
    path('jobs/<int:pk>/apply/', ApplyJobActionView.as_view(), name='apply_job'),
]
