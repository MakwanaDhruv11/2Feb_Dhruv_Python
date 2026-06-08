from django.db import models

class AboutInfo(models.Model):
    name = models.CharField(max_length=100, default="[YOUR_NAME]")
    role = models.CharField(max_length=100, default="[YOUR_ROLE]")
    tagline = models.TextField(default="[YOUR_TAGLINE]")
    bio = models.TextField(default="[YOUR_BIO]")
    experience_summary = models.CharField(max_length=100, default="[YOUR_EXPERIENCE]")
    location = models.CharField(max_length=100, default="[YOUR_LOCATION]")
    resume = models.FileField(upload_to='resume/', blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile/', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "About Info"

class Skill(models.Model):
    name = models.CharField(max_length=50)
    icon_class = models.CharField(max_length=50, help_text="FontAwesome or DevIcon class", blank=True)
    proficiency = models.IntegerField(default=80, help_text="Percentage 0-100")
    category = models.CharField(max_length=50, choices=[('Frontend', 'Frontend'), ('Backend', 'Backend'), ('Tools', 'Tools')], default='Frontend')

    def __str__(self):
        return self.name

class Project(models.Model):
    project_name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='projects/')
    tech_stack = models.CharField(max_length=200, help_text="Comma separated skills")
    github_url = models.URLField(blank=True, null=True)
    live_demo_url = models.URLField(blank=True, null=True)
    featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.project_name

    class Meta:
        ordering = ['order', '-id']

class Experience(models.Model):
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    start_date = models.CharField(max_length=50, help_text="e.g. Jan 2020")
    end_date = models.CharField(max_length=50, help_text="e.g. Dec 2022 or Present")
    description = models.TextField()

    def __str__(self):
        return f"{self.title} at {self.company}"

    class Meta:
        verbose_name_plural = "Experience"

class SocialLink(models.Model):
    platform = models.CharField(max_length=50)
    url = models.URLField()
    icon_class = models.CharField(max_length=50, help_text="FontAwesome class e.g. fab fa-github")

    def __str__(self):
        return self.platform

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"
