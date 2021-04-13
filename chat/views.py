import json
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from faker import Faker
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import ChatGrant

from .models import Room

fake = Faker()


def chat_users(request):
    users = User.objects.filter(is_superuser=False)
    response = []
    for user in users:
        r = dict()
        r["user_id"] = user.id
        r["fname"] = user.first_name
        r["lname"] = user.last_name
        r["country"] = user.profile.location
        r["timezone"] = user.profile.timezone
        r["profile_pic"] = user.profile.profile_pic.url
        r["is_online"] = user.profile.is_online
        response.append(r)

    return HttpResponse(json.dumps(response))


def user(request):
    user_id = request.GET.get('user_id')
    user = User.objects.get(id=user_id)
    response = {
        "username": user.username,
        "fname": user.first_name,
        "lname": user.last_name,
        "profile_pic": user.profile.profile_pic.url
    }
    return HttpResponse(json.dumps(response))


def all_rooms(request):
    rooms = Room.objects.all()
    return render(request, 'panotek/index.html', {'rooms': rooms})


def room_detail(request, slug):
    room = Room.objects.get(slug=slug)
    return render(request, 'chat/room_detail.html', {'room': room})


def token(request):
    from_user_id = request.GET.get('from_user_id', None)
    to_user_id = request.GET.get('to_user_id', None)
    device_id = request.GET.get('device', 'default')  # unique device ID
    from_user_name = User.objects.get(id=from_user_id).first_name
    to_user_name = User.objects.get(id=to_user_id).first_name

    room_id = min(from_user_id, to_user_id) + "--" + \
        max(from_user_id, to_user_id)

    account_sid = settings.TWILIO_ACCOUNT_SID
    api_key = settings.TWILIO_API_KEY
    api_secret = settings.TWILIO_API_SECRET
    chat_service_sid = settings.TWILIO_CHAT_SERVICE_SID

    token = AccessToken(account_sid, api_key, api_secret,
                        identity=from_user_name)

    # Create a unique endpoint ID for the device
    endpoint = "MyDjangoChatRoom:{0}:{1}".format(room_id, device_id)

    if chat_service_sid:
        chat_grant = ChatGrant(endpoint_id=endpoint,
                               service_sid=chat_service_sid)
        token.add_grant(chat_grant)

    response = {
        'from_user_name': from_user_name,
        'to_user_name': to_user_name,
        'identity': room_id,
        'token': token.to_jwt().decode('utf-8')
    }

    print("Response: ", response)

    return JsonResponse(response)
