# core/views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse

def password_gateway(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == 'dating2025':  # Change this password as needed
            request.session['authenticated'] = True
            return redirect('home')  # This now points to /home/
        else:
            return render(request, 'password_gateway.html', {'error': 'Invalid password'})
    
    # If already authenticated, redirect to home
    if request.session.get('authenticated'):
        return redirect('home')  # This now points to /home/
        
    return render(request, 'password_gateway.html')
