from django.contrib import admin
from .models import Notification, NotificationSetting

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')

class NotificationSettingAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_alerts', 'daily_digest', 'job_alerts')
    list_filter = ('email_alerts', 'daily_digest', 'job_alerts')
    search_fields = ('user__username',)

admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotificationSetting, NotificationSettingAdmin)
