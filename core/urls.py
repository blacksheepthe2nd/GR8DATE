# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from core.views import password_gateway

urlpatterns = [
    # Password gateway at root
    path("", password_gateway, name="password_gateway"),
    
    # Admin
    path("admin/", admin.site.urls),

    # Home page (accessible after password)
    path("home/", TemplateView.as_view(template_name="pages/index.html"), name="home"),

    # Include other pages
    path("", include("pages.urls")),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
