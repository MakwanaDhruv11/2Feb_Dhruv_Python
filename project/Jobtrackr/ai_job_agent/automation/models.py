from django.db import models
from django.conf import settings
from resumes.models import Resume
from jobs.models import Job

class CoverLetter(models.Model):
    """
    Model representing generated cover letters customized for specific jobs and resumes.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cover_letters'
    )
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='cover_letters'
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='cover_letters'
    )
    content = models.TextField(help_text="Full text content of the generated cover letter")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Cover Letter - {self.job.title} at {self.job.company}"
