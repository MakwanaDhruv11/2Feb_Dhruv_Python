from django.contrib import admin
from .models import AboutInfo, Skill, Project, Experience, SocialLink, ContactMessage

@admin.register(AboutInfo)
class AboutInfoAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Allow only one instance of AboutInfo
        if self.model.objects.count() > 0:
            return False
        return super().has_add_permission(request)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'proficiency')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'featured', 'order')
    list_editable = ('featured', 'order')

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'start_date', 'end_date')

@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('platform', 'url')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    readonly_fields = ('name', 'email', 'message', 'created_at')
