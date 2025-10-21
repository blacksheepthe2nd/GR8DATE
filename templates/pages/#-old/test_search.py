import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from pages.views import search_view

# Create a test request
factory = RequestFactory()
request = factory.get('/search/?q=mia')
request.user = get_user_model().objects.first()

print("=== TESTING SEARCH FUNCTION ===")
print(f"Search query: mia")
print(f"User: {request.user}")

try:
    response = search_view(request)
    print(f"Response status: {response.status_code}")
    
    # Check what data was passed to template
    context = response.context_data
    if context:
        print(f"Total results: {context.get('total', 0)}")
        page_obj = context.get('page_obj')
        if page_obj:
            print(f"Profiles on page: {len(page_obj.object_list)}")
            for profile in page_obj.object_list:
                print(f"  - {profile.user.username}: {profile.location}")
        else:
            print("No page_obj in context")
    else:
        print("No context data")
        
except Exception as e:
    print(f"ERROR: {e}")

print("=== END TEST ===")
