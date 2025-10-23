import os
import django
import sys

sys.path.append('/Users/carlsng/Projects')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from pages.models import Profile

# Check the specific user "coco-baby"
try:
    user = User.objects.get(username='coco-baby')
    profile = Profile.objects.get(user=user)
    
    print(f"Profile data for coco-baby:")
    print(f"  Location: '{profile.location}'")
    print(f"  Headline: '{profile.headline}'")
    print(f"  About: '{profile.about}'")
    print(f"  My Gender: '{profile.my_gender}'")
    print(f"  Looking For: '{profile.looking_for}'")
    print(f"  My Interests: '{profile.my_interests}'")
    print(f"  Date of Birth: '{profile.date_of_birth}'")
    print(f"  Age (calculated): {profile.age if hasattr(profile, 'age') else 'N/A'}")
    print(f"  Children: '{profile.children}'")
    print(f"  Smoking: '{profile.smoking}'")
    print(f"  Drinking: '{profile.drinking}'")
    print(f"  Exercise: '{profile.exercise}'")
    print(f"  Pets: '{profile.pets}'")
    print(f"  Diet: '{profile.diet}'")
    print(f"  Preferred Age Min: {profile.preferred_age_min}")
    print(f"  Preferred Age Max: {profile.preferred_age_max}")
    print(f"  Preferred Intent: '{profile.preferred_intent}'")
    print(f"  Preferred Distance: '{profile.preferred_distance}'")
    
except User.DoesNotExist:
    print("User coco-baby not found")
except Profile.DoesNotExist:
    print("Profile for coco-baby not found")
