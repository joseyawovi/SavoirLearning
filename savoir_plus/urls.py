"""
URL configuration for Savoir+ LMS project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from lms.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('django-admin/', admin.site.urls),  # Keep default admin as backup
    path('', include('lms.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)