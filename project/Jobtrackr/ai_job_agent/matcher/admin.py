from django.contrib import admin
from .models import JobMatch

class JobMatchAdmin(admin.ModelAdmin):
    list_display = ('resume', 'job', 'match_score', 'created_at')
    list_filter = ('match_score', 'created_at')
    search_fields = ('resume__user__username', 'job__title', 'job__company')

admin.site.register(JobMatch, JobMatchAdmin)
