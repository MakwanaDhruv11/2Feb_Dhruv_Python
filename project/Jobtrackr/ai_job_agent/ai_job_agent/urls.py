from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('resumes/', include('resumes.urls')),
    path('jobs/', include('jobs.urls')),
    path('matcher/', include('matcher.urls')),
    path('applications/', include('applications.urls')),
    path('notifications/', include('notifications.urls')),
    path('automation/', include('automation.urls')),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
