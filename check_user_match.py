import os
import django
import sys

sys.path.append('/Users/carlsng/Projects')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

media_path = "media/profiles/"
user_folders = [f for f in os.listdir(media_path) if f.startswith('user_')]
user_ids_from_folders = [int(f.split('_')[1]) for f in user_folders]

user_ids_from_db = list(User.objects.values_list('id', flat=True))

print("=== DIAGNOSTIC REPORT ===")
print(f"User folders found: {len(user_ids_from_folders)}")
print(f"Users in database: {len(user_ids_from_db)}")

missing_users = set(user_ids_from_folders) - set(user_ids_from_db)
print(f"Users with folders but no DB records: {len(missing_users)}")

if missing_users:
    print(f"First 10 missing user IDs: {sorted(list(missing_users))[:10]}")

if user_ids_from_db:
    print(f"First 10 DB user IDs: {user_ids_from_db[:10]}")
else:
    print("NO USERS IN DATABASE!")

if User.objects.filter(id=1).exists():
    user1 = User.objects.get(id=1)
    print(f"User 1 details: {user1.username} (ID: {user1.id})")
