from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile
import requests
import json

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.create(user=user, role=role)
        return redirect('/login/')
    return render(request, 'signup.html')

def home(request):
    return render(request, 'index.html')

def consult(request):
    return render(request, 'consult.html')

@csrf_exempt
def consult_ai(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        body = json.loads(request.body)
        message = body.get("message", "").strip()
        flask_response = requests.post(
            "http://localhost:5001/ask",
            json={"question": message},
            timeout=30
        )
        ai_data = flask_response.json()
        answer = ai_data.get("answer", "Sorry, could not process your request.")
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
    else:
        return "General Legal Query"
       
def lawyers(request):
    return render(request, 'lawyers.html')

def appointments(request):
    return render(request, 'appointments.html')

def lawyer_register(request):
    return render(request, 'lawyer-register.html')

def login_view(request):
    return render(request, 'login.html')

def book_appointment(request, lawyer_id=None):
    return render(request, 'book.html')