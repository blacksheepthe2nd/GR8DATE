import os
import shutil
from django.conf import settings

def upload_media():
    # Copy entire media folder to staticfiles
    media_src = 'media'
    media_dest = 'staticfiles/media'
    
    if os.path.exists(media_src):
        print("📁 Copying media files...")
        if os.path.exists(media_dest):
            shutil.rmtree(media_dest)
        shutil.copytree(media_src, media_dest)
        print(f"✅ All media files copied to {media_dest}")
        
        # Count files for verification
        total_files = sum([len(files) for r, d, files in os.walk(media_dest)])
        print(f"📊 Total media files deployed: {total_files}")
    else:
        print("❌ Media folder not found")

if __name__ == "__main__":
    upload_media()
