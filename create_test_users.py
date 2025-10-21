# create_test_users.py
import os
import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.contrib.auth import get_user_model
from pages.models import Profile, ProfileImage
from django.utils import timezone
from datetime import datetime, timedelta
import random

def download_image(url):
    """Download image from URL and return File object"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(response.content)
            img_temp.flush()
            return img_temp
    except:
        return None
    return None

def create_test_users():
    User = get_user_model()
    
    # Australian cities and suburbs
    australian_locations = [
        "Sydney, NSW", "Melbourne, VIC", "Brisbane, QLD", "Perth, WA", 
        "Adelaide, SA", "Gold Coast, QLD", "Canberra, ACT", "Newcastle, NSW",
        "Sunshine Coast, QLD", "Wollongong, NSW", "Geelong, VIC", "Hobart, TAS",
        "Townsville, QLD", "Cairns, QLD", "Darwin, NT", "Toowoomba, QLD",
        "Ballarat, VIC", "Bendigo, VIC", "Launceston, TAS", "Mackay, QLD"
    ]
    
    # Diverse profile data
    first_names = [
        "Sarah", "Emma", "Chloe", "Olivia", "Sophie", "Mia", "Charlotte", "Zoe",
        "Liam", "Noah", "William", "James", "Lucas", "Benjamin", "Alexander", "Ethan",
        "Ava", "Isabella", "Ruby", "Grace", "Emily", "Lily", "Amelia", "Ella"
    ]
    
    last_names = [
        "Smith", "Jones", "Williams", "Brown", "Wilson", "Taylor", "Johnson", "White",
        "Martin", "Anderson", "Thompson", "Nguyen", "Lee", "King", "Green", "Harris",
        "Clark", "Lewis", "Robinson", "Walker", "Hall", "Young", "Allen", "Wright"
    ]
    
    genders = ["Male", "Female", "Non-binary"]
    looking_for_options = ["Men", "Women", "Everyone"]
    interests = [
        "Hiking, Coffee, Travel", "Movies, Cooking, Art", "Sports, Music, Photography",
        "Reading, Yoga, Nature", "Dancing, Food, Adventure", "Gaming, Tech, Science",
        "Beach, Surfing, Sunsets", "Wine, Fine dining, Theater", "Fitness, Health, Meditation",
        "Animals, Volunteering, Culture"
    ]
    
    # Image URLs - using diverse, realistic people images from Pexels
    image_urls = [
        # Female images
        "https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg",
        "https://images.pexels.com/photos/1239291/pexels-photo-1239291.jpeg",
        "https://images.pexels.com/photos/718978/pexels-photo-718978.jpeg",
        "https://images.pexels.com/photos/1130626/pexels-photo-1130626.jpeg",
        "https://images.pexels.com/photos/1181686/pexels-photo-1181686.jpeg",
        "https://images.pexels.com/photos/1102341/pexels-photo-1102341.jpeg",
        "https://images.pexels.com/photos/1181690/pexels-photo-1181690.jpeg",
        "https://images.pexels.com/photos/3769021/pexels-photo-3769021.jpeg",
        "https://images.pexels.com/photos/3618028/pexels-photo-3618028.jpeg",
        "https://images.pexels.com/photos/3768689/pexels-photo-3768689.jpeg",
        
        # Male images  
        "https://images.pexels.com/photos/1222271/pexels-photo-1222271.jpeg",
        "https://images.pexels.com/photos/2379004/pexels-photo-2379004.jpeg",
        "https://images.pexels.com/photos/2182970/pexels-photo-2182970.jpeg",
        "https://images.pexels.com/photos/2379005/pexels-photo-2379005.jpeg",
        "https://images.pexels.com/photos/3777943/pexels-photo-3777943.jpeg",
        "https://images.pexels.com/photos/3778605/pexels-photo-3778605.jpeg",
        "https://images.pexels.com/photos/3777946/pexels-photo-3777946.jpeg",
        "https://images.pexels.com/photos/3777935/pexels-photo-3777935.jpeg",
        "https://images.pexels.com/photos/3777949/pexels-photo-3777949.jpeg",
        "https://images.pexels.com/photos/3778607/pexels-photo-3778607.jpeg",
        
        # Additional diverse images
        "https://images.pexels.com/photos/3785079/pexels-photo-3785079.jpeg",
        "https://images.pexels.com/photos/3785077/pexels-photo-3785077.jpeg",
        "https://images.pexels.com/photos/3785074/pexels-photo-3785074.jpeg",
        "https://images.pexels.com/photos/3785075/pexels-photo-3785075.jpeg"
    ]
    
    print("Creating 24 test users...")
    
    created_users = []
    
    for i in range(24):
        # Create unique username and email
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        username = f"{first_name.lower()}{last_name.lower()}{i+1}"
        email = f"{username}@example.com"
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"User {username} already exists, skipping...")
            continue
            
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password="newpass123",
            first_name=first_name,
            last_name=last_name
        )
        
        # Create profile
        profile = Profile.objects.create(user=user)
        
        # Set profile attributes
        profile.headline = f"Looking for meaningful connections in {random.choice(australian_locations).split(',')[0]}"
        profile.about = f"Hi! I'm {first_name}, a {random.choice(['creative', 'adventurous', 'ambitious', 'caring', 'passionate'])} person who loves {random.choice(interests)}. I'm excited to meet new people and see where life takes us!"
        profile.location = random.choice(australian_locations)
        profile.my_gender = random.choice(genders)
        profile.looking_for = random.choice(looking_for_options)
        profile.my_interests = random.choice(interests)
        profile.children = random.choice(["Don't want kids", "Want kids", "Open to kids", "Have kids"])
        
        # Set realistic age (18-65)
        age = random.randint(18, 65)
        birth_year = datetime.now().year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        profile.date_of_birth = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
        
        # Set preferences
        profile.preferred_age_min = max(18, age - 10)
        profile.preferred_age_max = min(65, age + 10)
        profile.preferred_intent = random.choice(["Dating", "Relationship", "Friendship", "Marriage"])
        profile.preferred_distance = random.choice(["10km", "25km", "50km", "100km", "Anywhere"])
        
        # Set approval status (first 20 approved, last 4 unapproved)
        if i < 20:
            profile.is_approved = True
            profile.is_complete = True
        else:
            profile.is_approved = False
            profile.is_complete = False
            
        profile.save()
        
        # Add profile images (1-6 images per user, mix of public and private)
        num_images = random.randint(1, 6)
        print(f"Adding {num_images} images for {username}...")
        
        images_added = 0
        for img_idx in range(num_images):
            if img_idx < len(image_urls):
                img_temp = download_image(image_urls[img_idx])
                if img_temp:
                    profile_image = ProfileImage(profile=profile)
                    # Make some images private (about 30% chance)
                    profile_image.is_private = random.random() < 0.3
                    profile_image.image.save(f"{username}_img{img_idx+1}.jpg", File(img_temp))
                    profile_image.save()
                    images_added += 1
                    print(f"  - Added {'PRIVATE' if profile_image.is_private else 'PUBLIC'} image {img_idx+1}")
        
        created_users.append({
            'username': username,
            'password': 'newpass123',
            'approved': profile.is_approved,
            'images': images_added,
            'location': profile.location
        })
        
        print(f"Created user: {username} | Approved: {profile.is_approved} | Images: {images_added} | Location: {profile.location}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total users created: {len(created_users)}")
    print(f"Approved users: {len([u for u in created_users if u['approved']])}")
    print(f"Unapproved users: {len([u for u in created_users if not u['approved']])}")
    
    print(f"\n=== USER CREDENTIALS ===")
    for user in created_users:
        status = "APPROVED" if user['approved'] else "UNAPPROVED"
        print(f"{user['username']} | Password: newpass123 | {status} | Images: {user['images']} | Location: {user['location']}")

if __name__ == "__main__":
    create_test_users()
