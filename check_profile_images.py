import os
import django
import sys

sys.path.append('/Users/carlsng/Projects')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from pages.models import Profile, ProfileImage

# Check a specific user
user = User.objects.get(username='coco-baby')
profile = Profile.objects.get(user=user)

print(f"Profile fields for {user.username}:")
for field in Profile._meta.get_fields():
    print(f"  {field.name}: {getattr(profile, field.name, 'N/A')}")

print(f"\nProfile images for {user.username}:")
images = ProfileImage.objects.filter(profile=profile)
for img in images:
    print(f"  Image: {img.image} (private: {img.is_private})")

# Check if there's a primary image method
if hasattr(profile, 'primary_image'):
    print(f"\nPrimary image: {profile.primary_image}")
