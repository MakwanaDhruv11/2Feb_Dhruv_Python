from django.db import models
from django.conf import settings
from resumes.models import Resume
from jobs.models import Job

class JobMatch(models.Model):
    """
    Model representing AI matching analytics between a user's resume and a job listing.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='matches'
    )
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='job_matches'
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='resume_matches'
    )
    
    match_score = models.IntegerField(default=0, help_text="AI match score from 0 to 100")
    match_explanation = models.TextField(blank=True, help_text="AI analysis details and recommendations")
    
    skills_matched = models.JSONField(default=list, blank=True, help_text="Skills found in both resume and job listing")
    skills_missing = models.JSONField(default=list, blank=True, help_text="Skills requested in job listing but missing from resume")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('resume', 'job')
        ordering = ['-match_score', '-created_at']

    def __str__(self):
        return f"{self.user.username} matched to {self.job.title} - Score: {self.match_score}%"
