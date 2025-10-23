import os
import django
import sys
import pandas as pd

sys.path.append('/Users/carlsng/Projects')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from pages.models import Profile

# Read the CSV from Downloads
csv_path = os.path.expanduser('~/Downloads/gr8date_complete_profiles.csv')
df = pd.read_csv(csv_path)

print("IMPORTING PROFILE DATA FROM CSV")

success_count = 0
for _, row in df.iterrows():
    username = row['username']
    
    try:
        user = User.objects.get(username=username)
        
        # Get or create profile
        profile, created = Profile.objects.get_or_create(user=user)
        
        # Update profile fields from CSV
        if pd.notna(row.get('display_name')):
            profile.display_name = row['display_name']
        if pd.notna(row.get('location')):
            profile.location = row['location']
        if pd.notna(row.get('age')):
            profile.age = int(row['age']) if pd.notna(row['age']) else None
        if pd.notna(row.get('bio')):
            profile.bio = row['bio']
        if pd.notna(row.get('headline')):
            profile.headline = row['headline']
        if pd.notna(row.get('about')):
            profile.about = row['about']
        if pd.notna(row.get('my_interests')):
            profile.interests = row['my_interests']
        
        # Gender fields
        if pd.notna(row.get('gender')):
            profile.gender = row['gender']
        if pd.notna(row.get('my_gender')):
            profile.my_gender = row['my_gender']
        if pd.notna(row.get('looking_for')):
            profile.looking_for_gender = row['looking_for']
            
        # Lifestyle fields
        if pd.notna(row.get('smoking')):
            profile.smoking = row['smoking']
        if pd.notna(row.get('drinking')):
            profile.drinking = row['drinking']
        if pd.notna(row.get('exercise')):
            profile.exercise = row['exercise']
        if pd.notna(row.get('pets')):
            profile.pets = row['pets']
        if pd.notna(row.get('diet')):
            profile.diet = row['diet']
        if pd.notna(row.get('children')):
            profile.children = row['children']
            
        # Preferences
        if pd.notna(row.get('preferred_age_min')):
            profile.preferred_age_min = int(row['preferred_age_min']) if pd.notna(row['preferred_age_min']) else 18
        if pd.notna(row.get('preferred_age_max')):
            profile.preferred_age_max = int(row['preferred_age_max']) if pd.notna(row['preferred_age_max']) else 60
        if pd.notna(row.get('preferred_distance')):
            profile.preferred_distance = int(row['preferred_distance']) if pd.notna(row['preferred_distance']) else 50
        if pd.notna(row.get('preferred_intent')):
            profile.preferred_intent = row['preferred_intent']
            
        profile.save()
        
        print(f"Updated profile for: {username}")
        success_count += 1
        
    except User.DoesNotExist:
        print(f"User not found: {username}")
    except Exception as e:
        print(f"Error updating {username}: {e}")

print(f"COMPLETED: Updated {success_count} profiles")
