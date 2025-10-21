# pages/middleware.py
from __future__ import annotations

from django.shortcuts import redirect


class PreviewLockMiddleware:
    """
    If a user is authenticated but not fully approved/complete, redirect them
    to /preview/ when they try to access protected app areas.

    Public pages are whitelisted and never redirected:
      - /, /index/ (home/marketing)
      - /login/, /join/, /auth/*, /logout/
      - /preview/ (obviously)
      - /blog/* (public content)
      - /static/*, /media/* (assets)
      - /admin/*, /accounts/*

    Protected areas (redirect to /preview/ if not approved+complete):
      - /messages/, /matches/, /hotdates/, /settings/

    Special cases while in preview (NOT redirected):
      - /dashboard/                      → show restricted dashboard shell
      - /profile/create/, /profile/preview/ → allow finishing/previewing profile
    """

    PROTECTED_PREFIXES = (
        "/messages/",
        "/matches/",
        "/hotdates/",
        "/settings/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Always allow static/media
        if path.startswith("/static/") or path.startswith("/media/"):
            return self.get_response(request)

        # Not logged in ⇒ do nothing
        user = getattr(request, "user", None)
        if not (user and user.is_authenticated):
            return self.get_response(request)

        # Profile / approval check (NOTE: uses is_approved)
        try:
            profile = user.profile
            is_complete = bool(getattr(profile, "is_complete", False))
            approved = bool(getattr(profile, "is_approved", False))  # ← uses is_approved
        except Exception:
            is_complete = False
            approved = False

        has_full_access = is_complete and approved
        if has_full_access:
            return self.get_response(request)

        # === Preview-mode rules ===

        # Public/auth/admin-like pages are always allowed
        if (
            path == "/" or
            path == "/index/" or
            path.startswith("/login/") or
            path.startswith("/join/") or
            path.startswith("/auth/") or
            path.startswith("/preview/") or
            path.startswith("/blog/") or
            path.startswith("/admin/") or
            path.startswith("/accounts/")
        ):
            return self.get_response(request)

        # Allow the dashboard shell to render (templates should use preview_mode to restrict UI)
        if path.startswith("/dashboard/"):
            return self.get_response(request)

        # Allow finishing/previewing the profile
        if path.startswith("/profile/create/") or path.startswith("/profile/preview/"):
            return self.get_response(request)

        # Any other profile subpaths are locked in preview
        if path.startswith("/profile/"):
            return redirect("preview")

        # Protected areas go to preview
        if any(path.startswith(p) for p in self.PROTECTED_PREFIXES):
            return redirect("preview")

        # Everything else: allow
        return self.get_response(request)

