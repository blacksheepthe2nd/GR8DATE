from django.shortcuts import render, redirect
from django.http import HttpResponse

def password_gateway(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == 'dating2025':  
            request.session['authenticated'] = True
            return redirect('home')
        else:
            return render(request, 'password_gateway.html', {'error': 'Invalid password'})
    
    # If already authenticated, redirect to home
    if request.session.get('authenticated'):
        return redirect('home')
        
    return render(request, 'password_gateway.html')
