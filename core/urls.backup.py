from pathlib import Path

from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView, RedirectView
from django.views.static import serve as static_serve
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage

BASE_DIR = Path(__file__).resolve().parent.parent

urlpatterns = [
    path("admin/", admin.site.urls),

    # Favicon → /static/favicon.png (optional: add static/favicon.png)
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("favicon.png"), permanent=True),
        name="favicon",
    ),

    # Public pages (your templates)
    path("", TemplateView.as_view(template_name="pages/index.html"), name="home"),
    path("index/", TemplateView.as_view(template_name="pages/index.html"), name="index"),
    path("index.html", TemplateView.as_view(template_name="pages/index.html"), name="index_html"),

    path("about/", TemplateView.as_view(template_name="pages/aboutus.html"), name="about"),
    path("aboutus.html", TemplateView.as_view(template_name="pages/aboutus.html"), name="aboutus_html"),

    path("contact/", TemplateView.as_view(template_name="pages/contact.html"), name="contact"),
    path("contact.html", TemplateView.as_view(template_name="pages/contact.html"), name="contact_html"),

    path("faq/", TemplateView.as_view(template_name="pages/faq.html"), name="faq"),
    path("faq.html", TemplateView.as_view(template_name="pages/faq.html"), name="faq_html"),

    path("privacy/", TemplateView.as_view(template_name="pages/privacy.html"), name="privacy"),
    path("privacy.html", TemplateView.as_view(template_name="pages/privacy.html"), name="privacy_html"),

    path("terms/", TemplateView.as_view(template_name="pages/terms.html"), name="terms"),
    path("terms.html", TemplateView.as_view(template_name="pages/terms.html"), name="terms_html"),

    path("join/", TemplateView.as_view(template_name="pages/join_gr8date_singlepw_show.html"), name="join"),
    path("signup/", TemplateView.as_view(template_name="pages/join_gr8date_singlepw_show.html"), name="signup"),
    path("login/", TemplateView.as_view(template_name="pages/login_gr8date_user_or_email_showpw.html"), name="login"),

    # Blog app (dynamic list/detail)
    path("", include("pages.urls")),
]

# Dev-only static mappings so your existing HTML paths work as-is
if settings.DEBUG:
    # Serve uploaded media
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Map /images/* → static/images/*
    urlpatterns += [
        re_path(
            r"^images/(?P<path>.*)$",
            static_serve,
            {"document_root": BASE_DIR / "static" / "images"},
            name="dev-images",
        ),
        re_path(
            r"^css/(?P<path>.*)$",
            static_serve,
            {"document_root": BASE_DIR / "static" / "css"},
            name="dev-css",
        ),
        re_path(
            r"^js/(?P<path>.*)$",
            static_serve,
            {"document_root": BASE_DIR / "static" / "js"},
            name="dev-js",
        ),
    ]

