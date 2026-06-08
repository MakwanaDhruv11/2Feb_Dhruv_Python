from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class Notification(models.Model):
    """
    Model representing notifications/alerts dispatched to users.
    """
    TYPES = (
        ('match', 'AI Match Alert'),
        ('job_alert', 'New Job Posting'),
        ('digest', 'Daily Digest Summary'),
        ('system', 'System Alert'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPES, default='system')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title} ({'Read' if self.is_read else 'Unread'})"


class NotificationSetting(models.Model):
    """
    Model representing user communication alert preferences.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_settings'
    )
    email_alerts = models.BooleanField(default=True, help_text="Send email alerts instantly")
    daily_digest = models.BooleanField(default=True, help_text="Compile and send daily digest emails")
    job_alerts = models.BooleanField(default=True, help_text="Notify when matching jobs are found")

    def __str__(self):
        return f"Preferences for {self.user.username}"


# Signals to automatically construct preferences configuration upon user signup
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_notification_settings(sender, instance, created, **kwargs):
    if created:
        NotificationSetting.objects.get_or_create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_notification_settings(sender, instance, **kwargs):
    if hasattr(instance, 'notification_settings'):
        instance.notification_settings.save()
    else:
        NotificationSetting.objects.get_or_create(user=instance)
