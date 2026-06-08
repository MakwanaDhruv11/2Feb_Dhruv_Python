from django.urls import path
from .views import (
    NotificationListView, NotificationMarkReadView,
    NotificationMarkAllReadView, NotificationSettingsUpdateView
)

app_name = 'notifications'

urlpatterns = [
    path('', NotificationListView.as_view(), name='notif_list'),
    path('<int:pk>/read/', NotificationMarkReadView.as_view(), name='notif_read'),
    path('read-all/', NotificationMarkAllReadView.as_view(), name='notif_read_all'),
    path('settings/', NotificationSettingsUpdateView.as_view(), name='notif_settings'),
]
