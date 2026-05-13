from django.shortcuts import render , redirect
from django.contrib.auth.models import User
from .models import UserProfile
# Create your views here.

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.create(user=user, role=role)

        return redirect('/login/')

    return render(request, 'signup.html')