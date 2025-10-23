import os
import django
import sys

sys.path.append('/Users/carlsng/Projects')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from pages.models import Profile

print("CREATING MISSING PROFILES FOR ALL USERS")

users = User.objects.all()
created_count = 0
existing_count = 0

for user in users:
    try:
        # This will create the profile if it doesn't exist
        profile, created = Profile.objects.get_or_create(user=user)
        if created:
            print(f"Created profile for: {user.username}")
            created_count += 1
        else:
            existing_count += 1
    except Exception as e:
        print(f"Error creating profile for {user.username}: {e}")

print(f"COMPLETED: {created_count} new profiles created, {existing_count} already existed")
print(f"Total users: {users.count()}, Total profiles: {Profile.objects.count()}")
