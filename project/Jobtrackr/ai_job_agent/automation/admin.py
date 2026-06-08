from django.contrib import admin
from .models import CoverLetter

class CoverLetterAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'job__title', 'job__company')

admin.site.register(CoverLetter, CoverLetterAdmin)
