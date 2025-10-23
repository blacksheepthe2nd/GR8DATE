import os
import django
import sys
import json

sys.path.append('/Users/carlsng/Projects')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from pages.models import Profile, ProfileImage

print("LINKING PROFILE IMAGES WITH MAPPING (FIXED)")

# Load the mapping - convert keys to integers
with open('user_id_mapping.json', 'r') as f:
    mapping_str = json.load(f)
    mapping = {int(k): v for k, v in mapping_str.items()}  # Convert string keys to integers

print(f"Loaded mapping for {len(mapping)} users")

media_path = "media/profiles/"
success_count = 0

for folder_name in os.listdir(media_path):
    if not folder_name.startswith('user_'):
        continue
        
    # Extract user ID from folder name (user_XXX)
    try:
        csv_id = int(folder_name.split('_')[1])
    except:
        print(f"  Skipping invalid folder: {folder_name}")
        continue
        
    # Get database ID from mapping
    if csv_id not in mapping:
        print(f"  No mapping found for CSV ID {csv_id}")
        continue
        
    db_id = mapping[csv_id]
    
    # Find user in database
    try:
        user = User.objects.get(id=db_id)
        profile, created = Profile.objects.get_or_create(user=user)
    except User.DoesNotExist:
        print(f"  User ID {db_id} not found in database")
        continue

    images_linked = 0
    user_folder = os.path.join(media_path, folder_name)
    
    # Link profile images
    profile_path = os.path.join(user_folder, 'profile')
    if os.path.exists(profile_path):
        for img_file in os.listdir(profile_path):
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                img_path = f"profiles/{folder_name}/profile/{img_file}"
                ProfileImage.objects.get_or_create(
                    profile=profile,
                    image=img_path,
                    defaults={'is_private': False}
                )
                images_linked += 1
    
    # Link additional images  
    additional_path = os.path.join(user_folder, 'additional')
    if os.path.exists(additional_path):
        for img_file in os.listdir(additional_path):
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                img_path = f"profiles/{folder_name}/additional/{img_file}"
                ProfileImage.objects.get_or_create(
                    profile=profile,
                    image=img_path,
                    defaults={'is_private': False}
                )
                images_linked += 1
    
    # Link private images
    private_path = os.path.join(user_folder, 'private')
    if os.path.exists(private_path):
        for img_file in os.listdir(private_path):
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                img_path = f"profiles/{folder_name}/private/{img_file}"
                ProfileImage.objects.get_or_create(
                    profile=profile,
                    image=img_path,
                    defaults={'is_private': True}
                )
                images_linked += 1
    
    if images_linked > 0:
        print(f"Processing {folder_name} -> {user.username} (DB ID: {db_id})")
        print(f"    Linked {images_linked} images")
        success_count += 1

print(f"COMPLETED: Linked images for {success_count} users")
