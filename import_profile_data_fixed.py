import os
import django
import sys
import pandas as pd
from datetime import datetime

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
        
        # Update profile fields from CSV - only use actual database fields
        if pd.notna(row.get('location')):
            profile.location = str(row['location'])[:100]  # CharField limit
        
        if pd.notna(row.get('headline')):
            profile.headline = str(row['headline'])[:200]
        
        if pd.notna(row.get('about')):
            profile.about = str(row['about'])
        
        if pd.notna(row.get('my_interests')):
            profile.my_interests = str(row['my_interests'])[:200]
        
        # Gender fields
        if pd.notna(row.get('my_gender')):
            profile.my_gender = str(row['my_gender'])[:50]
        if pd.notna(row.get('looking_for')):
            profile.looking_for = str(row['looking_for'])[:50]
            
        # Lifestyle fields
        if pd.notna(row.get('smoking')):
            profile.smoking = str(row['smoking'])[:50]
        if pd.notna(row.get('drinking')):
            profile.drinking = str(row['drinking'])[:50]
        if pd.notna(row.get('exercise')):
            profile.exercise = str(row['exercise'])[:50]
        if pd.notna(row.get('pets')):
            profile.pets = str(row['pets'])[:50]
        if pd.notna(row.get('diet')):
            profile.diet = str(row['diet'])[:50]
        if pd.notna(row.get('children')):
            profile.children = str(row['children'])[:50]
            
        # Preferences
        if pd.notna(row.get('preferred_age_min')):
            try:
                profile.preferred_age_min = int(row['preferred_age_min'])
            except (ValueError, TypeError):
                profile.preferred_age_min = 18
        
        if pd.notna(row.get('preferred_age_max')):
            try:
                profile.preferred_age_max = int(row['preferred_age_max'])
            except (ValueError, TypeError):
                profile.preferred_age_max = 60
                
        if pd.notna(row.get('preferred_distance')):
            profile.preferred_distance = str(row['preferred_distance'])[:50]
            
        if pd.notna(row.get('preferred_intent')):
            profile.preferred_intent = str(row['preferred_intent'])[:50]
        
        # Date of birth from age or dob field
        if pd.notna(row.get('dob')):
            try:
                # Try to parse date string
                dob = pd.to_datetime(row['dob'])
                profile.date_of_birth = dob.date()
            except:
                pass
        elif pd.notna(row.get('age')):
            try:
                # Calculate approximate DOB from age
                age = int(row['age'])
                current_year = datetime.now().year
                birth_year = current_year - age
                profile.date_of_birth = datetime(birth_year, 1, 1).date()
            except (ValueError, TypeError):
                pass
        
        # Must have tags
        if pd.notna(row.get('must_have_tags')):
            profile.must_have_tags = str(row['must_have_tags'])[:200]
            
        # Mark as complete if we have basic data
        if (profile.location or profile.about or profile.headline):
            profile.is_complete = True
            
        profile.save()
        
        print(f"Updated profile for: {username}")
        success_count += 1
        
    except User.DoesNotExist:
        print(f"User not found: {username}")
    except Exception as e:
        print(f"Error updating {username}: {e}")

print(f"COMPLETED: Updated {success_count} profiles")
