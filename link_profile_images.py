import pandas as pd
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/carlsng/Projects')
django.setup()

from django.contrib.auth import get_user_model
from django.apps import apps

User = get_user_model()
Profile = apps.get_model('pages', 'Profile')
ProfileImage = apps.get_model('pages', 'ProfileImage')

def link_profile_images():
    media_base = '/Users/carlsng/Projects/media/profiles'
    
    print("LINKING PROFILE IMAGES")
    
    linked_count = 0
    
    for user_dir in os.listdir(media_base):
        if user_dir.startswith('user_'):
            user_id = user_dir.replace('user_', '')
            
            try:
                user = User.objects.get(id=int(user_id))
                print(f"Processing user_{user_id}: {user.username}")
                
                profile, created = Profile.objects.get_or_create(user=user)
                if created:
                    print(f"  Created profile for {user.username}")
                
                profile_images_path = os.path.join(media_base, user_dir, 'profile')
                additional_images_path = os.path.join(media_base, user_dir, 'additional')
                private_images_path = os.path.join(media_base, user_dir, 'private')
                
                image_count = 0
                
                for category, path in [('profile', profile_images_path), 
                                      ('additional', additional_images_path),
                                      ('private', private_images_path)]:
                    if os.path.exists(path):
                        for image_file in os.listdir(path):
                            if image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                                image_path = os.path.join(path, image_file)
                                relative_path = f"media/profiles/{user_dir}/{category}/{image_file}"
                                
                                profile_image, img_created = ProfileImage.objects.get_or_create(
                                    profile=profile,
                                    image=relative_path,
                                    defaults={'is_private': (category == 'private')}
                                )
                                
                                if img_created:
                                    print(f"    Added {category} image: {image_file}")
                                    image_count += 1
                
                print(f"  Total images linked: {image_count}")
                linked_count += 1
                
            except User.DoesNotExist:
                print(f"  User {user_id} not found in database")
            except Exception as e:
                print(f"  Error processing user_{user_id}: {e}")
    
    print(f"COMPLETED: Linked images for {linked_count} users")

if __name__ == "__main__":
    link_profile_images()
