from django.contrib import admin
from .models import Job

class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'source', 'is_active', 'fetched_at')
    list_filter = ('source', 'is_active', 'fetched_at')
    search_fields = ('title', 'company', 'description')
    actions = ['make_inactive', 'make_active']

    @admin.action(description='Mark selected jobs as active')
    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Mark selected jobs as inactive')
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)

admin.site.register(Job, JobAdmin)
