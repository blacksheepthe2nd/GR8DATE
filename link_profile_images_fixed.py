import os
import django
import sys

sys.path.append('/Users/carlsng/Projects')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from pages.models import Profile, ProfileImage

print("LINKING PROFILE IMAGES (UPDATED)")

media_path = "media/profiles/"
success_count = 0

for item in os.listdir(media_path):
    if not item.startswith('user_'):
        continue  # Skip loose files
        
    user_folder = os.path.join(media_path, item)
    if not os.path.isdir(user_folder):
        continue  # Skip if it's not a directory
        
    # Extract user ID from folder name (user_XXX)
    try:
        user_id = int(item.split('_')[1])
    except:
        print(f"  Skipping invalid folder: {item}")
        continue
        
    # Find user in database
    try:
        user = User.objects.get(id=user_id)
        profile, created = Profile.objects.get_or_create(user=user)
    except User.DoesNotExist:
        print(f"  User {user_id} not found in database")
        continue

    images_linked = 0
    
    # Link profile images
    profile_path = os.path.join(user_folder, 'profile')
    if os.path.exists(profile_path):
        for img_file in os.listdir(profile_path):
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                img_path = f"profiles/{item}/profile/{img_file}"
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
                img_path = f"profiles/{item}/additional/{img_file}"
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
                img_path = f"profiles/{item}/private/{img_file}"
                ProfileImage.objects.get_or_create(
                    profile=profile,
                    image=img_path,
                    defaults={'is_private': True}
                )
                images_linked += 1
    
    if images_linked > 0:
        print(f"Processing {item}: {user.username}")
        print(f"    Linked {images_linked} images")
        success_count += 1

print(f"COMPLETED: Linked images for {success_count} users")
