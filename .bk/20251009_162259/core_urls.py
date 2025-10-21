# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from pages import views as pages  # use app views directly

urlpatterns = [
    # Root (marketing/index)
    path("", TemplateView.as_view(template_name="pages/index.html"), name="home"),

    # Admin
    path("admin/", admin.site.urls),

    # Auth entry points (render your existing templates)
    path("login/", TemplateView.as_view(template_name="pages/login_gr8date_user_or_email_showpw.html"), name="login"),
    path("join/",  TemplateView.as_view(template_name="pages/join_gr8date_singlepw_show.html"), name="join"),

    # Allauth (if installed)
    path("accounts/", include("allauth.urls")),

    # Safety alias (avoid 404s)
    path("accounts/profile/", TemplateView.as_view(template_name="pages/index.html")),

    # Auth handlers (form posts)
    path("auth/login", pages.auth_login_view, name="auth_login"),
    path("auth/signup", pages.auth_signup_view, name="auth_signup"),
    path("logout/", pages.logout_view, name="logout"),

    # Preview gate + dashboard
    path("preview/", pages.preview_gate, name="preview"),
    path("dashboard/", pages.dashboard, name="dashboard"),

    # Profile flow
    path("profile/create/", pages.profile_create, name="profile_create"),
    path("profile/preview/", pages.profile_preview, name="profile_preview"),
    # Public, read-only profile page (by id)
    path("profile/<int:pk>/", pages.profile_public, name="profile_public"),

    # Icon targets (non-messages live here)
    path("search/",   pages.search_view,   name="search"),
    path("matches/",  pages.matches_view,  name="matches"),

    # Hot Dates
    path("hotdates/",        pages.hotdates_list,   name="hotdates"),
    path("hotdates/list/",   pages.hotdates_list,   name="hotdates_list"),
    path("hotdates/create/", pages.hotdates_create, name="hotdates_create"),

    # Account
    path("settings/", pages.account_settings, name="account_settings"),

    # Blog
    path("blog/", pages.BlogListView.as_view(), name="blog_list"),
    path("blog/<slug:slug>/", pages.BlogDetailView.as_view(), name="blog_detail"),

    # Footer pages (so links don’t 404)
    path("about/",   TemplateView.as_view(template_name="pages/aboutus.html"), name="about"),
    path("contact/", TemplateView.as_view(template_name="pages/contact.html"), name="contact"),
    path("faq/",     TemplateView.as_view(template_name="pages/faq.html"), name="faq"),
    path("terms/",   TemplateView.as_view(template_name="pages/terms.html"), name="terms"),
    path("privacy/", TemplateView.as_view(template_name="pages/privacy.html"), name="privacy"),

    # Include app URLs (this brings in messages routes and block/unblock)
    path("", include("pages.urls")),
]

