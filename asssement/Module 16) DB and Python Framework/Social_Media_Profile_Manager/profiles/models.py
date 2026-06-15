from django.db import models

class UserProfile(models.Model):
    username = models.CharField(max_length=150, unique=True)
    age = models.IntegerField()
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.username
