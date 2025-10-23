import pandas as pd
import requests
import os

df = pd.read_csv('gr8date_complete_profiles.csv')

for index, row in df.iterrows():
    user_id = row['user_id']
    image_url = row['profile_image_url']
    
    if pd.notna(image_url):
        # Get the first image URL (they're semicolon-separated)
        first_image = image_url.split(';')[0].strip()
        filename = first_image.split('/')[-1]
        filepath = f"/Users/carlsng/Projects/media/profiles/user_{user_id}/{filename}"
        
        # Check if file already exists
        if not os.path.exists(filepath):
            print(f"Downloading image for user {user_id}...")
            try:
                response = requests.get(first_image)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
            except Exception as e:
                print(f"Failed to download for user {user_id}: {e}")
