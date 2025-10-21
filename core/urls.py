# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views  # ← ADD THIS IMPORT

from core.views import password_gateway

from pages.allauth_shim import ShimLoginView, ShimSignupView
from pages import views as pages

urlpatterns = [
    # Root (marketing/index)
    path("", TemplateView.as_view(template_name="pages/index.html"), name="home"),

    # Admin
    path("admin/", admin.site.urls),

    # Auth entry points (support both /login/ and /auth/login/)
    path("login/", ShimLoginView.as_view(), name="login"),
    path("auth/login/", ShimLoginView.as_view(), name="auth_login"),
    path("join/", ShimSignupView.as_view(), name="join"),
    
    # ← ADD LOGOUT URL HERE
    path("logout/", auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # ⚠️ REMOVED THE PROBLEMATIC PREVIEW ROUTE ✅
    # path("preview/", TemplateView.as_view(template_name="pages/preview.html"), name="preview"),

    # Allauth
    path("accounts/", include("allauth.urls")),
    path("accounts/profile/", TemplateView.as_view(template_name="pages/index.html")),

    # Footer pages
    path("about/", TemplateView.as_view(template_name="pages/aboutus.html"), name="about"),
    path("contact/", TemplateView.as_view(template_name="pages/contact.html"), name="contact"),
    path("faq/", TemplateView.as_view(template_name="pages/faq.html"), name="faq"),
    path("terms/", TemplateView.as_view(template_name="pages/terms.html"), name="terms"),
    path("privacy/", TemplateView.as_view(template_name="pages/privacy.html"), name="privacy"),

    # Include ALL pages URLs (this should come LAST to avoid conflicts)
    path("", include("pages.urls")),
 
    # Password protection as root
    path("", password_gateway, name="password_gateway"),
    
    # Keep all your existing URLs below
    path("home/", TemplateView.as_view(template_name="pages/index.html"), name="home"),
    # ... rest of your URLs

]

# Serve static and media files in both development and production
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
