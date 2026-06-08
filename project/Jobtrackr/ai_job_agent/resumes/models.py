from django.db import models
from django.conf import settings

class Resume(models.Model):
    """
    Model representing a user's uploaded resume and its parsed data.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resumes'
    )
    file = models.FileField(upload_to='resumes/')
    raw_text = models.TextField(blank=True, help_text="Raw text extracted from PDF")
    
    # Structured fields parsed from resume
    parsed_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Parsed structured data (name, email, phone, skills, education, experience, projects, certifications, links, summary)"
    )
    
    is_parsed = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.user.username}'s Resume - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
