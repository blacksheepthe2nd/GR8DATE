import os
import sys
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Import local data to production'
    
    def handle(self, *args, **options):
        data_file = 'local_data.json'
        
        if os.path.exists(data_file):
            self.stdout.write('Importing clean data...')
            try:
                call_command('loaddata', data_file)
                self.stdout.write('✅ Data imported successfully!')
            except Exception as e:
                self.stdout.write(f'⚠️ Partial import completed with errors: {e}')
        else:
            # Fallback - create superusers only
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            superusers = [
                {'username': 'carlsng', 'email': 'carlsng@gr8date.com.au', 'password': 'gr8date1234'},
                {'username': 'seanfh', 'email': 'seanfh@gr8date.com.au', 'password': 'gr8date1234'},
            ]
            
            for user_data in superusers:
                if not User.objects.filter(username=user_data['username']).exists():
                    User.objects.create_superuser(**user_data)
                    self.stdout.write(f'✅ User {user_data["username"]} created!')
