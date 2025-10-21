import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from pages.models import Profile
from django.db.models import Q

print("=== DIRECT DATABASE TEST ===")

# Test the exact same query as search_view
q = 'mia'
qs = Profile.objects.filter(is_complete=True, is_approved=True).select_related("user").prefetch_related("images")

print(f"Total complete/approved profiles: {qs.count()}")

if q:
    qs = qs.filter(
        Q(user__username__icontains=q) |
        Q(headline__icontains=q) |
        Q(about__icontains=q) |
        Q(location__icontains=q)
    )
    print(f"After search filter: {qs.count()}")

# Show what we found
for profile in qs:
    print(f"FOUND: {profile.user.username}")
    print(f"  Location: {profile.location}")
    print(f"  Headline: {profile.headline}")
    print(f"  About: {profile.about}")
    print(f"  Complete: {profile.is_complete}")
    print(f"  Approved: {profile.is_approved}")
    print("---")

if qs.count() == 0:
    print("NO PROFILES FOUND!")
    print("Let me check all profiles:")
    all_profiles = Profile.objects.all()
    for p in all_profiles:
        print(f"  {p.user.username}: complete={p.is_complete}, approved={p.is_approved}")

print("=== END TEST ===")
