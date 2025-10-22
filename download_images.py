import pandas as pd
import requests
import os
from pathlib import Path
import time

print("🚀 IMAGE DOWNLOADER - EXTERNAL STORAGE")
print("=" * 50)

# Your external storage path
storage_path = "/Volumes/Storage"
csv_path = None

print(f"🔍 Searching in: {storage_path}")

# Search for the CSV file
search_locations = [
    f"{storage_path}/grouped_images_clean.csv",
    f"{storage_path}/Downloads/grouped_images_clean.csv", 
    f"{storage_path}/Documents/grouped_images_clean.csv",
    f"{storage_path}/data/grouped_images_clean.csv",
]

# Check direct paths first
for path in search_locations:
    if os.path.exists(path):
        csv_path = path
        print(f"✅ FOUND CSV: {path}")
        break

# If not found, search recursively
if not csv_path:
    print("🔍 Searching entire storage drive...")
    for root, dirs, files in os.walk(storage_path):
        if "grouped_images_clean.csv" in files:
            csv_path = os.path.join(root, "grouped_images_clean.csv")
            print(f"✅ FOUND CSV: {csv_path}")
            break

if not csv_path:
    print("❌ Could not find 'grouped_images_clean.csv' on the storage drive")
    print("💡 Please make sure the file exists and is named correctly")
    exit()

# Load the CSV
try:
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} users from CSV")
except Exception as e:
    print(f"❌ Failed to load CSV: {e}")
    exit()

# Create local directory for downloads
base_dir = Path("media/profiles")
base_dir.mkdir(parents=True, exist_ok=True)
print(f"✅ Created download directory: {base_dir}")

# Setup downloader
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
})

print("\n📥 STARTING DOWNLOADS...")
print("=" * 50)

# Test with first 3 users
test_users = df.head(3)
total_downloaded = 0

for i, row in test_users.iterrows():
    user_id = row['user_id']
    print(f"\n👤 User {user_id} ({i+1}/{len(test_users)})")
    
    user_dir = base_dir / f"user_{user_id}"
    user_dir.mkdir(exist_ok=True)
    
    urls = [url.strip() for url in row['images'].split(';') if url.strip()]
    print(f"   📷 {len(urls)} images to download")
    
    for j, url in enumerate(urls):
        try:
            # Get filename from URL
            filename = os.path.basename(url)
            if not filename or '.' not in filename:
                filename = f"image_{j:02d}.jpg"
            
            filepath = user_dir / filename
            
            print(f"   ⬇️  Downloading {j+1}/{len(urls)}: {filename}")
            
            # Download the image
            response = session.get(url, timeout=30)
            response.raise_for_status()
            
            # Save the file
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Check file size
            file_size = os.path.getsize(filepath) / 1024  # KB
            print(f"   ✅ Downloaded ({file_size:.1f}KB)")
            total_downloaded += 1
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
        
        # Small delay to be nice to the server
        time.sleep(0.5)

print("\n" + "=" * 50)
print(f"🎉 TEST COMPLETE!")
print(f"📊 Users processed: {len(test_users)}")
print(f"🖼️  Images downloaded: {total_downloaded}")
print(f"📁 Check results: ls -la media/profiles/")

# Show what was downloaded
print(f"\n📂 Downloaded folders:")
for user_dir in base_dir.iterdir():
    if user_dir.is_dir():
        images = list(user_dir.glob("*.*"))
        print(f"   {user_dir.name}: {len(images)} images")
