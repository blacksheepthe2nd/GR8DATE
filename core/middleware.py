# core/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class PasswordProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs that don't require password protection
        exempt_urls = [
            '/admin/',
            '/static/',
            '/media/',
            '/favicon.ico',
            '/robots.txt',
        ]
        
        # Check if current path is exempt
        current_path = request.path_info
        if any(current_path.startswith(url) for url in exempt_urls):
            return self.get_response(request)
        
        # Check if user needs to authenticate
        if not request.session.get('authenticated'):
            # Only redirect to password gateway if not already there
            if current_path != '/':
                return redirect('password_gateway')
        
        return self.get_response(request)
