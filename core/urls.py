# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from core.views import password_gateway

urlpatterns = [
    path("", password_gateway, name="password_gateway"),
    path("admin/", admin.site.urls),
    path("home/", TemplateView.as_view(template_name="pages/index.html"), name="home"),
    path("", include("pages.urls")),  # Keep this for other pages
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

