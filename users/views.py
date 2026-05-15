from django.shortcuts import render, redirect

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
import requests


# Create your views here.


def home(request):
    return render(request, 'index.html')


@csrf_exempt  # needed because JS fetch doesn't send Django's csrf token
def signup(request):
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
        user = User.objects.create_user(
            username=email, email=email, password=password)
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


@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)  # destroys the session
        return JsonResponse({'message': 'Logged out successfully'})

    return JsonResponse({'error': 'Invalid method'}, status=405)


# def dashboard(request):
#     if not request.user.is_authenticated:  # replaces @login_required
#         return JsonResponse({'error': 'Please login first'}, status=401)

#     return JsonResponse({
#         'message': 'Welcome to dashboard',
#         'email': request.user.email,
#         'name': request.user.first_name
#     })

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    return render(request, 'dashboard.html', {
        'name': request.user.first_name,
        'email': request.user.email,
    })


@csrf_exempt
def consult_ai(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        body = json.loads(request.body)
        message = body.get("message", "").strip()

        if not message:
            return JsonResponse({"error": "No message provided"}, status=400)

        # Call your Flask AI service
        flask_response = requests.post(
            "http://localhost:5001/ask",
            json={"question": message},
            timeout=30
        )

        ai_data = flask_response.json()
        answer = ai_data.get("answer", "Sorry, I could not process your request.")

        return JsonResponse({
            "reply": answer,
            "area": detect_legal_area(message),
            "recommended": [],
            "aiPowered": True
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def detect_legal_area(message):
    message = message.lower()
    if any(w in message for w in ["landlord", "rent", "deposit", "tenant"]):
        return "Property / Tenancy Law"
    elif any(w in message for w in ["fired", "job", "salary", "employer", "worker"]):
        return "Labor Law"
    elif any(w in message for w in ["divorce", "marriage", "wife", "husband", "child"]):
        return "Family Law"
    elif any(w in message for w in ["police", "arrest", "crime", "fir", "case"]):
        return "Criminal Law"
    elif any(w in message for w in ["company", "business", "contract", "agreement"]):
        return "Business / Contract Law"
    elif any(w in message for w in ["consumer", "product", "refund", "cheated"]):
        return "Consumer Protection Law"
    else:
        return "General Legal Query"
