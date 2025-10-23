import os
import django
import sys

sys.path.append('/Users/carlsng/Projects')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from pages.models import Profile

# Check what fields the Profile model actually has
print("Profile model fields:")
for field in Profile._meta.get_fields():
    print(f"  {field.name} ({field.get_internal_type()})")

# Check if we can create a profile
try:
    from django.contrib.auth.models import User
    user = User.objects.first()
    if user:
        profile, created = Profile.objects.get_or_create(user=user)
        print(f"\nSample profile for {user.username}:")
        print(f"  Display name: {profile.display_name}")
        print(f"  Bio: {getattr(profile, 'bio', 'No bio field')}")
        print(f"  Location: {getattr(profile, 'location', 'No location field')}")
except Exception as e:
    print(f"Error: {e}")
