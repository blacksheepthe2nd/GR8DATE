import os
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Import local data to production'
    
    def handle(self, *args, **options):
        # Path to your data file
        data_file = 'local_data.json'
        
        if os.path.exists(data_file):
            self.stdout.write('Importing data...')
            call_command('loaddata', data_file)
            self.stdout.write('✅ Data imported successfully!')
        else:
            self.stdout.write('❌ Data file not found!')
