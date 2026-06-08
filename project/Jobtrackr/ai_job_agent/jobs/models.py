from django.db import models

class Job(models.Model):
    """
    Model representing fetched job postings from various sources.
    Used for searching, filtering, and matching with resumes.
    """
    SOURCES = (
        ('remoteok', 'RemoteOK'),
        ('wellfound', 'Wellfound'),
        ('greenhouse', 'Greenhouse'),
        ('lever', 'Lever'),
        ('manual', 'Manually Added'),
    )

    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=20, choices=SOURCES, default='manual')
    url = models.URLField(max_length=1000, unique=True)
    description = models.TextField(blank=True)
    salary = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list, blank=True, help_text="Tags/Skills associated with the job")
    
    fetched_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fetched_at']
        indexes = [
            models.Index(fields=['source']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.title} at {self.company} ({self.get_source_display()})"
