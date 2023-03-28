from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.db import IntegrityError

def home(request):
    if request.method == "GET":
        #user = User.objects.create_user('lennon@thebeatles.com', 'johnpassword')
        #user.save()
        return render(request, "authuser/home.html")
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            print('found user')
            login(request, user)
            return render(request, "authuser/home.html")
        else:
            return render(request, "authuser/home.html", {"message":"couldn't find user account"})
        

def logoutview(request):
    if request.method == "POST":
        logout(request)
        return render(request, "authuser/logout.html")
    
def createaccount(request):
    if request.method == "GET":
        return render(request, "authuser/createaccount.html")
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        if password!=confirm_password:
            return render(request, "authuser/createaccount.html", {"message":"passwords don't match"})
        try:
            user = User.objects.create_user(email, password)
            user.save()
        except IntegrityError:
            return render(request, "authuser/createaccount.html", {"message":"email in use"})
        login(request, user)
        return render(request, "authuser/home.html")