import json
import requests

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def set_country_timezone(user, ip):
    # remove this for local testing
    # ip = '157.42.8.53'
    url = "http://ip-api.com/json/" + ip
    resp = requests.get(url)
    if resp.status_code == 200:
        resp = resp.json()
        if resp.get('status') == "success":
            country = resp["country"]
            tz = resp["timezone"]
            profile = user.profile
            profile.location = country
            profile.timezone = tz
            profile.save()


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
            ip = get_client_ip(request)
            set_country_timezone(user, ip)
            login(request, user)
            profile = user.profile
            profile.is_online = True
            profile.save()
            response["id"] = user.id
            response["fname"] = user.first_name
            response["status"] = True
            return HttpResponse(json.dumps(response))
        return HttpResponseForbidden("Invalid Username or Password")
    return HttpResponseBadRequest("Invalid Username or Password")


@csrf_exempt
def Logout(request):
    current_user_id = request.GET.get('current_user_id')
    try:
        user = User.objects.get(id=current_user_id)
        profile = user.profile
        profile.is_online = False
        profile.save()
    except Exception as e:
        pass
    logout(request)
    return HttpResponse("Logout Successfull")


@csrf_exempt
def CurrentUser(request):
    current_user_id = request.GET.get('current_user_id')
    user = None
    try:
        user = User.objects.get(id=current_user_id)
    except:
        pass
    response = {}
    response["status"] = False
    if user:
        response["status"] = True
        response["id"] = user.id
        response["fname"] = user.first_name
    return HttpResponse(json.dumps(response))
