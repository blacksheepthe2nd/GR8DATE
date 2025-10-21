# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from core.views import password_gateway
from pages.allauth_shim import ShimLoginView, ShimSignupView

urlpatterns = [
    # Password protection as ROOT - MUST BE FIRST
    path("", password_gateway, name="password_gateway"),
    
    # Admin (should work without password for admin access)
    path("admin/", admin.site.urls),

    # Auth entry points 
    path("login/", ShimLoginView.as_view(), name="login"),
    path("auth/login/", ShimLoginView.as_view(), name="auth_login"),
    path("join/", ShimSignupView.as_view(), name="join"),
    path("logout/", auth_views.LogoutView.as_view(next_page='password_gateway'), name='logout'),

    # Allauth
    path("accounts/", include("allauth.urls")),
    path("accounts/profile/", TemplateView.as_view(template_name="pages/index.html")),

    # Footer pages
    path("about/", TemplateView.as_view(template_name="pages/aboutus.html"), name="about"),
    path("contact/", TemplateView.as_view(template_name="pages/contact.html"), name="contact"),
    path("faq/", TemplateView.as_view(template_name="pages/faq.html"), name="faq"),
    path("terms/", TemplateView.as_view(template_name="pages/terms.html"), name="terms"),
    path("privacy/", TemplateView.as_view(template_name="pages/privacy.html"), name="privacy"),

    # Home page (accessible after password)
    path("home/", TemplateView.as_view(template_name="pages/index.html"), name="home"),

    # Include pages URLs but NOT at root to avoid conflicts
    path("pages/", include("pages.urls")),
]

# Serve static and media files in both development and production
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
