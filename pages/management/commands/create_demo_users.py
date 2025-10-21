# management/commands/create_demo_users.py
import random
from datetime import datetime
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from pages.models import Profile, ProfileImage
import requests
import time

User = get_user_model()

class Command(BaseCommand):
    help = 'Create 24 demo users (12 male, 12 female) with complete profiles and images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-existing',
            action='store_true',
            help='Delete existing demo users before creating new ones',
        )

    def handle(self, *args, **options):
        if options['delete_existing']:
            self.delete_existing_demo_users()

        self.create_demo_users()
        
    def delete_existing_demo_users(self):
        """Delete existing demo users to avoid duplicates"""
        demo_users = User.objects.filter(username__in=[
            'tom', 'harry', 'john', 'mike', 'dave', 'chris', 'alex', 'ryan', 'mark', 'steve', 'kevin', 'brian',
            'jane', 'sarah', 'emma', 'olivia', 'chloe', 'sophie', 'amelia', 'charlotte', 'mia', 'isabella', 'ava', 'lily'
        ])
        count = demo_users.count()
        demo_users.delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} existing demo users'))

    def create_demo_users(self):
        # Male user data - Australian locations
        male_users = [
            {
                'username': 'tom', 'first_name': 'Tom', 'last_name': 'Wilson', 'age': 28,
                'location': 'Sydney, NSW', 'headline': 'Adventure seeker and coffee lover',
                'about': 'Love hiking, good coffee, and deep conversations. Looking for someone to explore life with.',
                'interests': ['hiking', 'coffee', 'travel', 'photography', 'music'],
                'must_have': ['honest', 'adventurous', 'kind']
            },
            {
                'username': 'harry', 'first_name': 'Harry', 'last_name': 'Brown', 'age': 32,
                'location': 'Melbourne, VIC', 'headline': 'Professional with a passion for life',
                'about': 'Finance professional who enjoys golf, wine tasting, and weekend getaways.',
                'interests': ['golf', 'wine', 'travel', 'fitness', 'movies'],
                'must_have': ['ambitious', 'loyal', 'humorous']
            },
            {
                'username': 'john', 'first_name': 'John', 'last_name': 'Taylor', 'age': 25,
                'location': 'Gold Coast, QLD', 'headline': 'Surf instructor and beach enthusiast',
                'about': 'Spend my days in the ocean and my evenings watching sunsets. Looking for my beach partner.',
                'interests': ['surfing', 'beach', 'yoga', 'music', 'cooking'],
                'must_have': ['adventurous', 'compassionate', 'confident']
            },
            {
                'username': 'mike', 'first_name': 'Mike', 'last_name': 'Davis', 'age': 30,
                'location': 'Brisbane, QLD', 'headline': 'Tech geek and foodie',
                'about': 'Software developer by day, food explorer by night. Love trying new restaurants and tech gadgets.',
                'interests': ['technology', 'cooking', 'gaming', 'art', 'music'],
                'must_have': ['curious', 'kind', 'honest']
            },
            {
                'username': 'dave', 'first_name': 'Dave', 'last_name': 'Miller', 'age': 27,
                'location': 'Perth, WA', 'headline': 'Musician and nature lover',
                'about': 'Play in a local band and find inspiration in mountains and beaches.',
                'interests': ['music', 'hiking', 'beach', 'photography', 'books'],
                'must_have': ['creative', 'passionate', 'loyal']
            },
            {
                'username': 'chris', 'first_name': 'Chris', 'last_name': 'Anderson', 'age': 29,
                'location': 'Adelaide, SA', 'headline': 'Fitness coach and motivator',
                'about': 'Helping people become their best selves. Love outdoor workouts and healthy living.',
                'interests': ['fitness', 'health', 'travel', 'dogs', 'music'],
                'must_have': ['motivated', 'positive', 'kind']
            },
            {
                'username': 'alex', 'first_name': 'Alex', 'last_name': 'Thomas', 'age': 31,
                'location': 'Canberra, ACT', 'headline': 'Public servant and wine enthusiast',
                'about': 'Enjoy good food, great wine, and meaningful connections in the capital.',
                'interests': ['wine', 'cooking', 'politics', 'travel', 'art'],
                'must_have': ['sophisticated', 'honest', 'ambitious']
            },
            {
                'username': 'ryan', 'first_name': 'Ryan', 'last_name': 'Jackson', 'age': 26,
                'location': 'Byron Bay, NSW', 'headline': 'Marine biologist and conservationist',
                'about': 'Passionate about ocean conservation. Love diving, sailing, and marine life.',
                'interests': ['ocean', 'conservation', 'travel', 'photography', 'science'],
                'must_have': ['passionate', 'caring', 'adventurous']
            },
            {
                'username': 'mark', 'first_name': 'Mark', 'last_name': 'White', 'age': 33,
                'location': 'Melbourne, VIC', 'headline': 'Architect with an eye for beauty',
                'about': 'Designing spaces that inspire. Enjoy art galleries, modern architecture, and city exploration.',
                'interests': ['art', 'architecture', 'travel', 'design', 'photography'],
                'must_have': ['creative', 'detail-oriented', 'romantic']
            },
            {
                'username': 'steve', 'first_name': 'Steve', 'last_name': 'Harris', 'age': 28,
                'location': 'Sydney, NSW', 'headline': 'Chef and food entrepreneur',
                'about': 'Running a small bistro. Love creating memorable dining experiences.',
                'interests': ['cooking', 'food', 'travel', 'wine', 'music'],
                'must_have': ['passionate', 'creative', 'kind']
            },
            {
                'username': 'kevin', 'first_name': 'Kevin', 'last_name': 'Martin', 'age': 30,
                'location': 'Hobart, TAS', 'headline': 'Teacher and community volunteer',
                'about': 'High school teacher passionate about education and community development.',
                'interests': ['education', 'community', 'hiking', 'books', 'music'],
                'must_have': ['compassionate', 'patient', 'loyal']
            },
            {
                'username': 'brian', 'first_name': 'Brian', 'last_name': 'Lee', 'age': 29,
                'location': 'Darwin, NT', 'headline': 'Adventure guide and outdoorsman',
                'about': 'Leading tours in the Outback. Love camping, fishing, and exploring remote areas.',
                'interests': ['camping', 'fishing', 'adventure', 'photography', 'travel'],
                'must_have': ['adventurous', 'resourceful', 'honest']
            }
        ]

        # Female user data - Australian locations
        female_users = [
            {
                'username': 'jane', 'first_name': 'Jane', 'last_name': 'Johnson', 'age': 26,
                'location': 'Melbourne, VIC', 'headline': 'Art curator and coffee enthusiast',
                'about': 'Working in a contemporary art gallery. Love brunch, exhibitions, and city walks.',
                'interests': ['art', 'coffee', 'brunch', 'museums', 'travel'],
                'must_have': ['cultured', 'kind', 'curious']
            },
            {
                'username': 'sarah', 'first_name': 'Sarah', 'last_name': 'Williams', 'age': 29,
                'location': 'Sydney, NSW', 'headline': 'Marketing professional and beach lover',
                'about': 'Enjoy coastal walks, yoga, and trying new restaurants around Sydney.',
                'interests': ['yoga', 'beach', 'food', 'travel', 'fitness'],
                'must_have': ['positive', 'adventurous', 'loyal']
            },
            {
                'username': 'emma', 'first_name': 'Emma', 'last_name': 'Smith', 'age': 27,
                'location': 'Brisbane, QLD', 'headline': 'Teacher with a love for travel',
                'about': 'Primary school teacher who loves exploring new places during school holidays.',
                'interests': ['travel', 'education', 'reading', 'coffee', 'hiking'],
                'must_have': ['caring', 'patient', 'humorous']
            },
            {
                'username': 'olivia', 'first_name': 'Olivia', 'last_name': 'Brown', 'age': 31,
                'location': 'Perth, WA', 'headline': 'Marine scientist and sunset chaser',
                'about': 'Researching marine ecosystems and enjoying beautiful West Australian sunsets.',
                'interests': ['science', 'ocean', 'photography', 'hiking', 'wine'],
                'must_have': ['intelligent', 'passionate', 'kind']
            },
            {
                'username': 'chloe', 'first_name': 'Chloe', 'last_name': 'Davis', 'age': 28,
                'location': 'Gold Coast, QLD', 'headline': 'Yoga instructor and wellness coach',
                'about': 'Helping people find balance through yoga and mindful living.',
                'interests': ['yoga', 'wellness', 'meditation', 'beach', 'cooking'],
                'must_have': ['calm', 'compassionate', 'positive']
            },
            {
                'username': 'sophie', 'first_name': 'Sophie', 'last_name': 'Wilson', 'age': 30,
                'location': 'Adelaide, SA', 'headline': 'Wine maker and food lover',
                'about': 'Working in the Barossa Valley. Enjoy wine tasting, cooking, and entertaining.',
                'interests': ['wine', 'cooking', 'entertaining', 'travel', 'art'],
                'must_have': ['sophisticated', 'creative', 'romantic']
            },
            {
                'username': 'amelia', 'first_name': 'Amelia', 'last_name': 'Taylor', 'age': 25,
                'location': 'Byron Bay, NSW', 'headline': 'Digital nomad and surf enthusiast',
                'about': 'Working remotely while enjoying the beach lifestyle. Love surfing and morning yoga.',
                'interests': ['surfing', 'yoga', 'travel', 'technology', 'music'],
                'must_have': ['free-spirited', 'adventurous', 'genuine']
            },
            {
                'username': 'charlotte', 'first_name': 'Charlotte', 'last_name': 'Anderson', 'age': 32,
                'location': 'Canberra, ACT', 'headline': 'Policy advisor and book club host',
                'about': 'Enjoy intellectual conversations, wine bars, and weekend escapes to the coast.',
                'interests': ['books', 'politics', 'wine', 'travel', 'art'],
                'must_have': ['intelligent', 'articulate', 'loyal']
            },
            {
                'username': 'mia', 'first_name': 'Mia', 'last_name': 'Thomas', 'age': 29,
                'location': 'Sydney, NSW', 'headline': 'Graphic designer and art lover',
                'about': 'Creating beautiful designs by day, exploring galleries and cafes by weekend.',
                'interests': ['design', 'art', 'coffee', 'photography', 'travel'],
                'must_have': ['creative', 'observant', 'kind']
            },
            {
                'username': 'isabella', 'first_name': 'Isabella', 'last_name': 'Martin', 'age': 27,
                'location': 'Melbourne, VIC', 'headline': 'Musician and cafe hopper',
                'about': 'Playing in jazz clubs and discovering Melbournes best hidden cafes.',
                'interests': ['music', 'coffee', 'jazz', 'food', 'books'],
                'must_have': ['artistic', 'passionate', 'humorous']
            },
            {
                'username': 'ava', 'first_name': 'Ava', 'last_name': 'Harris', 'age': 31,
                'location': 'Hobart, TAS', 'headline': 'Chef and local produce advocate',
                'about': 'Running a farm-to-table restaurant. Love cooking with fresh Tasmanian ingredients.',
                'interests': ['cooking', 'food', 'farming', 'wine', 'travel'],
                'must_have': ['passionate', 'authentic', 'warm']
            },
            {
                'username': 'lily', 'first_name': 'Lily', 'last_name': 'Clark', 'age': 26,
                'location': 'Cairns, QLD', 'headline': 'Marine biologist and dive instructor',
                'about': 'Exploring the Great Barrier Reef and sharing its wonders with others.',
                'interests': ['diving', 'marine life', 'conservation', 'travel', 'photography'],
                'must_have': ['adventurous', 'caring', 'enthusiastic']
            }
        ]

        created_count = 0
        
        # Create male users
        for user_data in male_users:
            if self.create_user_profile(user_data, 'male', 'female'):
                created_count += 1

        # Create female users  
        for user_data in female_users:
            if self.create_user_profile(user_data, 'female', 'male'):
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} demo users with complete profiles!')
        )

    def create_user_profile(self, user_data, gender, looking_for_gender):
        """Create a single user with complete profile"""
        try:
            # Create user
            user = User.objects.create_user(
                username=user_data['username'],
                email=f"{user_data['username']}@example.com",
                password='password1234',  # Same password for all demo users
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )

            # Calculate date of birth from age
            today = datetime.now().date()
            dob = today.replace(year=today.year - user_data['age'])

            # Create profile
            profile = Profile.objects.create(
                user=user,
                date_of_birth=dob,
                headline=user_data['headline'],
                location=user_data['location'],
                about=user_data['about'],
                my_gender=gender,
                looking_for=looking_for_gender,
                children=random.choice(['yes', 'none', 'want', 'dont_want']),
                smoking=random.choice(['no', 'occasionally', 'yes']),
                drinking=random.choice(['no', 'socially', 'often']),
                exercise=random.choice(['never', 'sometimes', 'regularly']),
                pets=random.choice(['no_pets', 'cat', 'dog', 'other']),
                diet=random.choice(['anything', 'vegetarian', 'vegan', 'pescatarian']),
                my_interests=','.join(user_data['interests']),
                must_have_tags=','.join(user_data['must_have']),
                preferred_age_min=random.randint(24, 32),
                preferred_age_max=random.randint(33, 45),
                preferred_distance=random.choice(['10', '25', '50', '100', 'any']),
                preferred_intent=random.choice(['casual', 'longterm', 'friends', 'marriage']),
                is_complete=True,
                is_approved=True
            )

            # Download and create profile images
            self.create_profile_images(profile, gender)

            self.stdout.write(
                self.style.SUCCESS(f'Created {gender} user: {user_data["username"]} from {user_data["location"]}')
            )
            return True

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to create user {user_data["username"]}: {str(e)}')
            )
            return False

    def create_profile_images(self, profile, gender):
        """Download and create profile images for a user"""
        try:
            # Create primary profile image
            primary_url = self.get_random_image('primary')
            if primary_url:
                self.download_and_save_image(profile, primary_url, is_primary=True, is_private=False)

            # Create 2-3 additional public images
            for i in range(random.randint(2, 3)):
                additional_url = self.get_random_image('additional')
                if additional_url:
                    self.download_and_save_image(profile, additional_url, is_primary=False, is_private=False)
                    time.sleep(0.5)  # Be nice to the image service

            # Create 1-2 private images
            for i in range(random.randint(1, 2)):
                private_url = self.get_random_image('private')
                if private_url:
                    self.download_and_save_image(profile, private_url, is_primary=False, is_private=True)
                    time.sleep(0.5)

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Error creating images for {profile.user.username}: {str(e)}')
            )

    def get_random_image(self, image_type):
        """Get random image URL - reliable method without specific IDs"""
        base_url = "https://picsum.photos"
        
        # Different sizes for different types
        if image_type == 'primary':
            size = (400, 400)  # Square for profile
        else:
            size = (300, 400)  # Portrait for additional/private
        
        # Use random seed for variety but reliable URLs
        random_seed = random.randint(1, 1000)
        return f"{base_url}/seed/{random_seed}/{size[0]}/{size[1]}"

    def download_and_save_image(self, profile, image_url, is_primary=False, is_private=False):
        """Download image from URL and save as ProfileImage"""
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Create a filename
            filename = f"{profile.user.username}_{'primary' if is_primary else 'private' if is_private else 'additional'}_{random.randint(1000,9999)}.jpg"
            
            # Create ProfileImage instance
            profile_image = ProfileImage(
                profile=profile,
                is_primary=is_primary,
                is_private=is_private
            )
            
            # Save the image
            profile_image.image.save(
                filename,
                ContentFile(response.content),
                save=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Downloaded image for {profile.user.username}')
            )
            
            return profile_image
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Failed to download image from {image_url}: {str(e)}')
            )
            return None
