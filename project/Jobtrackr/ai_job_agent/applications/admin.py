from django.contrib import admin
from .models import SavedJob, Application

class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__username', 'job__title', 'job__company')

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'status', 'applied_at', 'updated_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('user__username', 'job__title', 'job__company')

admin.site.register(SavedJob, SavedJobAdmin)
admin.site.register(Application, ApplicationAdmin)
