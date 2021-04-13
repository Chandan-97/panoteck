import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Create your views here.


@csrf_exempt
def Login(request):
    response = {}
    response["status"] = False
    if(request.POST):
        login_data = request.POST.dict()
        username = login_data.get("email")
        password = login_data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            profile = user.profile
            profile.is_online = True
            profile.save()
            response["id"] = user.id
            response["status"] = True
            return HttpResponse(json.dumps(response))
        return HttpResponseForbidden(json.dumps(response))
    return HttpResponseBadRequest(json.dumps(response))


@csrf_exempt
def Logout(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        profile.is_online = False
        profile.save()
    logout(request)
    return HttpResponse("Logout Successfull")


@csrf_exempt
def CurrentUser(request):
    user = request.user
    response = {}
    response["status"] = False
    if user.is_authenticated:
        response["status"] = True
        response["id"] = user.id
    return HttpResponse(json.dumps(response))
