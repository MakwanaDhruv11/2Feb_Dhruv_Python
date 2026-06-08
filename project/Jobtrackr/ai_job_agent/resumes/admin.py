from django.contrib import admin
from .models import Resume

class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'file', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('user__username', 'file')

admin.site.register(Resume, ResumeAdmin)
