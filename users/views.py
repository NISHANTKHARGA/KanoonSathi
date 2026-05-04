from django.shortcuts import render, redirect
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from django.contrib.auth import login, logout, authenticate
# from django.contrib.auth.decorators import login_required

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import login,logout, authenticate

# Create your views here.

@csrf_exempt  # needed because JS fetch doesn't send Django's csrf token
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # reads the JSON sent by frontend

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        # check if user already exists
        if User.objects.filter(username=email).exists():
            return JsonResponse({'error': 'User already exists'}, status=400)

        # create the user
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        user.save()

        return JsonResponse({'message': 'Registration successful', 'email': email})

    # GET request - just show the page
    return render(request, 'signup.html')

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        user = authenticate(request, username=email, password=password)
    
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful', 'email': email})
        else:
            return JsonResponse({'error': 'Invalid email or password'}, status=401)
    
    # GET request - just show the page
    return render(request, 'login.html')


# def dashboard(request):
#     return render(request, 'index.html')
@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)  # destroys the session
        return JsonResponse({'message': 'Logged out successfully'})

    return JsonResponse({'error': 'Invalid method'}, status=405)


# def logout_view(request):
#     logout(request)
#     return redirect('login')
def dashboard(request):
    if not request.user.is_authenticated:  # replaces @login_required
        return JsonResponse({'error': 'Please login first'}, status=401)

    return JsonResponse({
        'message': 'Welcome to dashboard',
        'email': request.user.email,
        'name': request.user.first_name
    })
