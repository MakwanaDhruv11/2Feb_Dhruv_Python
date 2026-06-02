from django.db import models

class Doctor(models.Model):
    name = models.CharField(max_length=150)
    specialization = models.CharField(max_length=150)
    city = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.name} - {self.specialization}"
