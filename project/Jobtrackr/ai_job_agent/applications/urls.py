from django.urls import path
from .views import (
    ApplicationListView, ApplicationUpdateView, 
    ApplicationUpdateStatusView, ApplicationDeleteView,
    SavedJobDeleteView
)

app_name = 'applications'

urlpatterns = [
    path('', ApplicationListView.as_view(), name='tracker_list'),
    path('<int:pk>/edit/', ApplicationUpdateView.as_view(), name='tracker_edit'),
    path('<int:pk>/status/', ApplicationUpdateStatusView.as_view(), name='tracker_status_update'),
    path('<int:pk>/delete/', ApplicationDeleteView.as_view(), name='tracker_delete'),
    path('saved/<int:pk>/delete/', SavedJobDeleteView.as_view(), name='saved_delete'),
]
