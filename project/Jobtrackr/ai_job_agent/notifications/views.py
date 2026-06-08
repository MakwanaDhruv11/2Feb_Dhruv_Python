from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Notification, NotificationSetting

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 15

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Grab configuration settings
        context['settings'], _ = NotificationSetting.objects.get_or_create(user=self.request.user)
        return context


class NotificationMarkReadView(LoginRequiredMixin, View):
    """
    POST action to mark a notification as read.
    """
    def post(self, request, pk, *args, **kwargs):
        notif = get_object_or_404(Notification, pk=pk, user=request.user)
        notif.is_read = True
        notif.save()
        return redirect('notifications:notif_list')


class NotificationMarkAllReadView(LoginRequiredMixin, View):
    """
    POST action to mark all notifications as read.
    """
    def post(self, request, *args, **kwargs):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, "All notifications marked as read.")
        return redirect('notifications:notif_list')


class NotificationSettingsUpdateView(LoginRequiredMixin, View):
    """
    POST action to update notification settings.
    """
    def post(self, request, *args, **kwargs):
        settings_obj, _ = NotificationSetting.objects.get_or_create(user=request.user)
        settings_obj.email_alerts = 'email_alerts' in request.POST
        settings_obj.daily_digest = 'daily_digest' in request.POST
        settings_obj.job_alerts = 'job_alerts' in request.POST
        settings_obj.save()
        messages.success(request, "Notification preferences updated.")
        return redirect('notifications:notif_list')
