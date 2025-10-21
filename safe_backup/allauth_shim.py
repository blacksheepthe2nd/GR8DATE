# pages/allauth_shim.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_protect
from django.views.generic import View


def _ensure_profile(user):
    from pages.models import Profile
    try:
        return user.profile
    except Profile.DoesNotExist:
        return Profile.objects.create(user=user)


def _allow_full_access(profile) -> bool:
    # NOTE: uses is_approved
    return bool(getattr(profile, "is_complete", False) and getattr(profile, "is_approved", False))


@method_decorator(csrf_protect, name="dispatch")
class ShimLoginView(View):
    template_name = "pages/login_gr8date_user_or_email_showpw.html"

    def _target_url_name(self, user):
        prof = _ensure_profile(user)
        return "dashboard" if _allow_full_access(prof) else "preview"

    def get(self, request: HttpRequest) -> HttpResponse:
        # Already authenticated? Don’t show login—send to the right place.
        if request.user.is_authenticated:
            target = self._target_url_name(request.user)
            print(f"[login][GET] already authed → redirect {target}")
            return redirect(target)
        return render(request, self.template_name)

    def post(self, request: HttpRequest) -> HttpResponse:
        ident = (request.POST.get("identifier") or "").strip()
        password = request.POST.get("password") or ""
        raw_pw = password  # fallback

        # sanitize but keep raw fallback
        import unicodedata
        ZW = {"\u200b", "\u200c", "\u200d", "\u2060"}
        NBSP = {"\u00A0"}

        def sanitize(s: str) -> str:
            if not s:
                return s
            s = unicodedata.normalize("NFC", s)
            s = "".join(ch for ch in s if ch not in ZW and ch not in NBSP)
            return s.strip()

        ident_s = sanitize(ident)
        pass_s = sanitize(password)

        # resolve by email or username (case-insensitive)
        User = get_user_model()
        user = None
        if ident_s:
            if "@" in ident_s:
                user = User.objects.filter(email__iexact=ident_s).first()
            if not user:
                user = User.objects.filter(username__iexact=ident_s).first()

        s_ok = r_ok = False
        if user and getattr(user, "is_active", True):
            s_ok = user.check_password(pass_s)
            if not s_ok and raw_pw and raw_pw != pass_s:
                r_ok = user.check_password(raw_pw)

        print(
            f"[login][POST] ident='{ident}' user_found={bool(user)} "
            f"sanitized_ok={s_ok} raw_ok={r_ok}"
        )

        if user and (s_ok or r_ok):
            login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
            target = self._target_url_name(user)
            print(f"[login][POST] SUCCESS → redirect {target}")
            return redirect(target)

        messages.error(request, "Invalid credentials. Please try again.")
        print("[login][POST] FAIL → re-render login page (200)")
        return render(
            request,
            self.template_name,
            {"prefill_identifier": request.POST.get("identifier", "")},
            status=200,
        )


# =========================
# SIGNUP (email + password + 18+ checkbox)
# =========================
@dataclass
class SignupResult:
    user: Optional[object]
    error: Optional[str] = None


def _unique_username_from_email(email: str) -> str:
    base = slugify((email or "").split("@")[0]) or "user"
    User = get_user_model()
    cand = base[:24]
    if not User.objects.filter(username__iexact=cand).exists():
        return cand
    i = 2
    while True:
        u = f"{base}-{i}"[:30]
        if not User.objects.filter(username__iexact=u).exists():
            return u
        i += 1


def _do_signup(email: str, password: str, accepted: bool) -> SignupResult:
    if not email or not password:
        return SignupResult(None, "Please provide both email and password.")
    if not accepted:
        return SignupResult(None, "Please confirm you are 18+ and agree to the terms.")
    User = get_user_model()
    username = _unique_username_from_email(email)
    try:
        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.is_active = True
        user.save()
    except IntegrityError:
        return SignupResult(None, "An account with that email already exists.")
    except Exception:
        return SignupResult(None, "Could not create account. Please try again.")
    return SignupResult(user, None)


@method_decorator(csrf_protect, name="dispatch")
class ShimSignupView(View):
    template_name = "pages/join_gr8date_singlepw_show.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name)

    def post(self, request: HttpRequest) -> HttpResponse:
        email = (request.POST.get("email") or "").strip()
        password = (request.POST.get("password") or "").strip()

        # accept any checked checkbox (keeps your template untouched)
        accepted = any(
            (v in ("on", "true", "1"))
            for k, v in request.POST.items()
            if k not in {"email", "password", "csrfmiddlewaretoken"}
        )

        res = _do_signup(email, password, accepted)
        if res.error:
            messages.error(request, res.error)
            return render(
                request, self.template_name, {"prefill_email": email}, status=200
            )

        login(request, res.user, backend=settings.AUTHENTICATION_BACKENDS[0])
        _ensure_profile(res.user)
        messages.success(request, "Welcome! Your account was created.")
        return redirect("preview")

