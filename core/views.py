# core/views.py
from django.shortcuts import render, redirect

def password_gateway(request):
    # If already authenticated, redirect to home
    if request.session.get('authenticated'):
        return redirect('home')
    
    if request.method == 'POST':
        password = request.POST.get('password', '')
        if password == 'dating2025':
            request.session['authenticated'] = True
            return redirect('home')
        else:
            return render(request, 'password_gateway.html', {'error': 'Invalid password'})
    
    return render(request, 'password_gateway.html')
