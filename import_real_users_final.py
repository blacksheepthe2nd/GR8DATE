import pandas as pd
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/carlsng/Projects')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def import_real_users():
    df = pd.read_csv('/Users/carlsng/Downloads/gr8date_complete_profiles.csv')
    
    print("Total users in CSV:", len(df))
    print("Approved users:", (df['is_approved'] == True).sum())
    
    imported_count = 0
    skipped_count = 0
    
    for _, row in df.iterrows():
        try:
            if User.objects.filter(username=row['username']).exists():
                skipped_count += 1
                continue
            
            display_name = str(row.get('display_name', ''))[:30] if pd.notna(row.get('display_name')) else ''
            
            user = User.objects.create_user(
                username=row['username'],
                email=row['email'],
                password='default_password_123',
                first_name=display_name,
                is_active=bool(row.get('is_approved', False))
            )
            
            status = "ACTIVE" if user.is_active else "INACTIVE (not approved)"
            print(status + ":", row['username'], "(user_" + str(row['user_id']) + ")")
            imported_count += 1
            
        except Exception as e:
            print("Error creating", row['username'], ":", e)
    
    print("IMPORT SUMMARY")
    print("Imported:", imported_count)
    print("Skipped (already exist):", skipped_count)
    print("Total users in database now:", User.objects.count())
    print("Active users:", User.objects.filter(is_active=True).count())
    print("Inactive users:", User.objects.filter(is_active=False).count())

if __name__ == "__main__":
    import_real_users()
