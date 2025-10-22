import os
import django
import pandas as pd

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from pages.models import Profile

def import_profiles(csv_file_path):
    # Read the CSV
    df = pd.read_csv(csv_file_path)
    
    print(f"Importing {len(df)} profiles...")
    
    success_count = 0
    error_count = 0
    
    for index, row in df.iterrows():
        try:
            # Create or get User
            user, created = User.objects.get_or_create(
                username=row['username'],
                defaults={
                    'email': row['email'],
                    'first_name': row['display_name'].split(' ')[0] if ' ' in row['display_name'] else row['display_name'],
                }
            )
            
            if created:
                user.set_unusable_password()
                user.save()
            
            # Create Profile
            profile, profile_created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'date_of_birth': row['date_of_birth'],
                    'headline': row['headline'],
                    'location': row['location'],
                    'about': row['about'],
                    'my_gender': row['my_gender'],
                    'looking_for': row['looking_for'],
                    'children': row['children'],
                    'smoking': row['smoking'],
                    'drinking': row['drinking'],
                    'exercise': row['exercise'],
                    'pets': row['pets'],
                    'diet': row['diet'],
                    'my_interests': row['my_interests'],
                    'must_have_tags': row['must_have_tags'],
                    'preferred_age_min': row['preferred_age_min'],
                    'preferred_age_max': row['preferred_age_max'],
                    'preferred_distance': row['preferred_distance'],
                    'preferred_intent': row['preferred_intent'],
                    'is_complete': True,
                    'is_approved': row['is_approved'].lower() == 'true' if 'is_approved' in row else False,
                }
            )
            
            success_count += 1
            if (success_count + error_count) % 50 == 0:
                print(f"Processed {success_count + error_count}/{len(df)} profiles...")
                
        except Exception as e:
            error_count += 1
            print(f"Error with {row.get('username', 'unknown')}: {e}")
    
    print(f"\n🎉 Import completed!")
    print(f"✅ Success: {success_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📊 Total processed: {success_count + error_count}")

if __name__ == "__main__":
    csv_file = "gr8date_complete_profiles.csv"
    if os.path.exists(csv_file):
        import_profiles(csv_file)
    else:
        print(f"❌ CSV file not found: {csv_file}")
        print("Please make sure the CSV file is in the same directory as this script")
