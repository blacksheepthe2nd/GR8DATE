# core/views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse

def password_gateway(request):
    # Check if already authenticated via session
    if request.session.get('authenticated'):
        # If already authenticated, redirect to home
        return redirect('home')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == 'dating2025':  # Change this password as needed
            # Set session variable and mark session as modified
            request.session['authenticated'] = True
            request.session.modified = True
            # Redirect to home page
            return redirect('home')
        else:
            return render(request, 'password_gateway.html', {'error': 'Invalid password'})
    
    # If GET request and not authenticated, show password form
    return render(request, 'password_gateway.html')
