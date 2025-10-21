# core/views.py
from django.shortcuts import render, redirect

def password_gateway(request):
    # If user submits password
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == 'dating2025':
            request.session['authenticated'] = True
            request.session.set_expiry(86400)  # 24 hours
            return redirect('home')  # Go to home page after login
        else:
            return render(request, 'password_gateway.html', {'error': 'Invalid password'})
    
    # If GET request, just show the password form
    return render(request, 'password_gateway.html')
