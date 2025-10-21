from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pages.models import Profile
from datetime import date
import random

class Command(BaseCommand):
    help = 'Create 12 sample Australian profiles'

    def handle(self, *args, **options):
        sample_profiles = [
            {'username': 'sarah_adventurer', 'gender': 'female', 'location': 'Sydney, NSW', 'age': 28},
            {'username': 'mike_tech', 'gender': 'male', 'location': 'Melbourne, VIC', 'age': 32},
            {'username': 'emma_yoga', 'gender': 'female', 'location': 'Brisbane, QLD', 'age': 26},
            {'username': 'jake_surf', 'gender': 'male', 'location': 'Byron Bay, NSW', 'age': 30},
            {'username': 'chloe_artist', 'gender': 'female', 'location': 'Perth, WA', 'age': 29},
            {'username': 'liam_music', 'gender': 'male', 'location': 'Adelaide, SA', 'age': 31},
            {'username': 'olivia_doctor', 'gender': 'female', 'location': 'Canberra, ACT', 'age': 34},
            {'username': 'noah_teacher', 'gender': 'male', 'location': 'Gold Coast, QLD', 'age': 29},
            {'username': 'ava_writer', 'gender': 'female', 'location': 'Hobart, TAS', 'age': 27},
            {'username': 'lucas_engineer', 'gender': 'male', 'location': 'Newcastle, NSW', 'age': 33},
            {'username': 'isla_chef', 'gender': 'female', 'location': 'Sunshine Coast, QLD', 'age': 26},
            {'username': 'ethan_farmer', 'gender': 'male', 'location': 'Margaret River, WA', 'age': 35},
        ]

        created_count = 0
        
        for data in sample_profiles:
            if User.objects.filter(username=data['username']).exists():
                self.stdout.write(f"User {data['username']} already exists, skipping...")
                continue

            try:
                email = f"greatdate76+{data['username']}@gmail.com"
                user = User.objects.create_user(
                    username=data['username'],
                    email=email,
                    password='Thedogsrdogs2!'
                )
                
                profile = Profile.objects.create(
                    user=user,
                    headline=f"Adventurous person from {data['location']}",
                    about=f"Love exploring Australia and meeting new people. Based in {data['location']} and looking for genuine connections.",
                    location=data['location'],
                    my_gender=data['gender'],
                    looking_for='male' if data['gender'] == 'female' else 'female',
                    my_interests='travel,coffee,reading,music,outdoors',
                    is_complete=True,
                    is_approved=True
                )
                
                today = date.today()
                birth_year = today.year - data['age']
                profile.date_of_birth = date(birth_year, random.randint(1, 12), random.randint(1, 28))
                profile.save()
                
                self.stdout.write(self.style.SUCCESS(f"Created {data['gender']} profile: {data['username']}"))
                created_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to create {data['username']}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} sample profiles!"))
        self.stdout.write("Login with: greatdate76+username@gmail.com")
        self.stdout.write("Password: Thedogsrdogs2!")
