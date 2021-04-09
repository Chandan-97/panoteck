from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Create your views here.


@csrf_exempt
def Login(request):
    if(request.POST):
        login_data = request.POST.dict()
        username = login_data.get("email")
        password = login_data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return HttpResponse("Logged In")
        return HttpResponseForbidden("Invalid email or password")
    return HttpResponseBadRequest("Not found")


@csrf_exempt
def Logout(request):
    logout(request)
    return HttpResponse("Logout Successfull")
