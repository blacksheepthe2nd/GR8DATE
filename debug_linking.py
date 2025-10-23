import os
import django
import sys

sys.path.append('/Users/carlsng/Projects')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

print("=== DEBUGGING USER FOLDERS ===")

# Check user folders
media_path = "media/profiles/"
user_folders = [f for f in os.listdir(media_path) if f.startswith('user_')]
print(f"Found {len(user_folders)} user folders")
print(f"First 5 folders: {user_folders[:5]}")

# Check what's inside one folder
if user_folders:
    sample_folder = user_folders[0]
    print(f"\nContents of {sample_folder}:")
    sample_path = os.path.join(media_path, sample_folder)
    if os.path.exists(sample_path):
        for item in os.listdir(sample_path):
            item_path = os.path.join(sample_path, item)
            print(f"  {item} (dir: {os.path.isdir(item_path)})")

print("\n=== DEBUGGING DATABASE USERS ===")
# Check database users
users = User.objects.all()
print(f"Total users in DB: {users.count()}")
print("First 10 users:")
for user in users[:10]:
    print(f"  ID: {user.id}, Username: {user.username}")

# Check if any user IDs match the folders
folder_ids = [int(f.split('_')[1]) for f in user_folders if f.split('_')[1].isdigit()]
db_ids = list(User.objects.values_list('id', flat=True))

matching_ids = set(folder_ids) & set(db_ids)
print(f"\nMatching user IDs between folders and DB: {len(matching_ids)}")
if matching_ids:
    print(f"First 10 matches: {sorted(list(matching_ids))[:10]}")
