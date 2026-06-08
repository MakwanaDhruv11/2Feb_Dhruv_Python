from django.db import models
from django.conf import settings
from jobs.models import Job

class SavedJob(models.Model):
    """
    Model representing jobs saved/bookmarked by users.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_jobs'
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='saved_by_users'
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"


class Application(models.Model):
    """
    Model representing job applications tracked by users.
    """
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('interviewing', 'Interviewing'),
        ('offered', 'Offered'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    notes = models.TextField(blank=True, help_text="Personal notes or reminders about this application")
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.user.username} applied to {self.job.title} ({self.get_status_display()})"
