import json
import pytz
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.db.models import Q
from datetime import datetime, timedelta
from faker import Faker
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import ChatGrant
from django.views.decorators.csrf import csrf_exempt

from .models import Room, Message
from main.models import OfficeLocation

fake = Faker()


def get_is_online(user):
    if user.profile.is_online == False:
        return False
    now = pytz.utc.localize(datetime.now())
    if user.last_login and user.last_login >= now - timedelta(hours=8):
        return True
    return False


def count_pending_messages(to_user, from_user):
    pending_messages_count = Message.objects.filter(from_user=from_user, to_user=to_user, status=Message.SENT).count()
    return pending_messages_count


def get_timezone(tz):
    try:
        now = datetime.now(pytz.timezone(tz))
        tz = now.strftime('%z')[:3] + ":" + now.strftime('%z')[3:] + ", " + now.strftime("%H:%m")
    except:
        pass
    return tz


def get_office_loc(profile):
    loc = profile.office_loc
    if loc:
        return {
            "id": loc.id,
            "loc": loc.loc,
            "logo": loc.logo.url if loc.logo else None
        }
    return {}


def chat_users(request):
    current_user_id = request.GET.get('current_user_id')
    current_user = User.objects.get(id=current_user_id)

    user = User.objects.get(is_superuser=False, first_name__iexact="Receptionist")
    response = []
    ids = []
    if user:
        r = dict()
        profile = user.profile
        r["user_id"] = user.id
        ids.append(user.id)
        r["fname"] = user.first_name
        r["lname"] = user.last_name
        r["country"] = "--"
        r["timezone"] = "--"
        r["profile_pic"] = request.build_absolute_uri(profile.profile_pic.url)
        r["office_loc"] = profile.office_loc
        r["is_online"] = get_is_online(user)
        r["pending_messages_count"] = count_pending_messages(to_user=current_user, from_user=user)
        response.append(r)

    users = User.objects.filter(is_superuser=False).exclude(id__in=ids)
    for user in users:
        r = dict()
        profile = user.profile
        r["user_id"] = user.id
        r["fname"] = user.first_name
        r["lname"] = user.last_name
        r["country"] = profile.location
        r["timezone"] = get_timezone(profile.timezone)
        r["profile_pic"] = request.build_absolute_uri(profile.profile_pic.url)
        r["office_loc"] = get_office_loc(profile)
        r["is_online"] = get_is_online(user)
        r["pending_messages_count"] = count_pending_messages(to_user=current_user, from_user=user)
        response.append(r)

    return HttpResponse(json.dumps(response))


def list_location(request):
    locations = OfficeLocation.objects.all()
    loc = []
    for l in locations:
        loc.append({
            "id": l.id,
            "loc": l.loc,
            "logo": l.logo.url if l.logo else None
        })

    return HttpResponse(json.dumps(loc))


def set_location(request):
    current_user_id = request.GET.get('current_user_id')
    user = User.objects.get(id=current_user_id)
    id = request.GET["id"]
    profile = user.profile
    loc = OfficeLocation.objects.get(id=id)
    profile.office_loc = loc
    profile.save()
    return HttpResponse("Saved")


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
    return render(request, 'panoteck/index.html', {'rooms': rooms})


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

@csrf_exempt
def send_message(request):
    data = request.POST
    type = data["type"]
    from_user_id = data["from_user_id"]

    if type == "online_status":
        profile = User.objects.get(id=from_user_id).profile
        profile.is_online = data['status']
        profile.save()
        print("Status offline")

    elif type == "chat":
        to_user_id = data["to_user_id"]
        body = data["body"]
        from_user = User.objects.get(id=from_user_id)
        to_user = User.objects.get(id=to_user_id)
        Message(from_user=from_user, to_user=to_user, body=body).save()
        return HttpResponse(body)

def receive_message(request):
    data = request.GET
    from_user_id = data["from_user_id"]
    from_user = User.objects.get(id=from_user_id)

    to_user_id = data["to_user_id"]
    to_user = User.objects.get(id=to_user_id)

    status = data.get("status")

    if status is None:
        messages = Message.objects.filter(Q(from_user=from_user, to_user=to_user)
                                          | Q(from_user=to_user, to_user=from_user)).order_by("created_at")[:100]
    else:
        messages = Message.objects.filter(Q(from_user=from_user, to_user=to_user, status=status)
                                          | Q(from_user=to_user, to_user=from_user, status=status)).order_by("created_at")[:100]

    msg = []
    for message in messages:
        msg.append({
            "from_user_id": message.from_user.id,
            "from_user_name": message.from_user.first_name,
            "to_user_id": message.to_user.id,
            "to_user_name": message.to_user.first_name,
            "body": message.body
        })

    Message.objects.filter(
        from_user=to_user, to_user=from_user, status=Message.SENT
    ).update(status=Message.RECEIVED)

    return HttpResponse(json.dumps(msg))


def poll_new_messages(request):
    data = request.GET
    from_user_id = data["from_user_id"]
    from_user = User.objects.get(id=from_user_id)

    to_user_id = data["to_user_id"]
    to_user = User.objects.get(id=to_user_id)

    new_messages = Message.objects.filter(from_user_id=from_user_id, to_user_id=to_user_id, status=Message.SENT).order_by("created_at")
    msg = []
    for message in new_messages:
        msg.append({
            "from_user_id": message.from_user.id,
            "from_user_name": message.from_user.first_name,
            "to_user_id": message.to_user.id,
            "to_user_name": message.to_user.first_name,
            "body": message.body
        })
    Message.objects.filter(
        from_user=from_user, to_user=to_user, status=Message.SENT
    ).update(status=Message.RECEIVED)
    return HttpResponse(json.dumps(msg))


def poll_data(request):
    current_user_id = request.GET.get('current_user_id')
    current_user = None
    try:
        current_user = User.objects.get(id=current_user_id)
    except:
        pass
    if not current_user:
        response = {"status": False, "data": []}
        return HttpResponse(json.dumps(response))
    user_ids = User.objects.filter(is_superuser=False).values("id")
    user_data = {}
    for id in user_ids:
        # online_status
        id = id.get('id')
        user = User.objects.get(id=id)

        user_data[id] = {
            "is_online": get_is_online(user),
            "pending_messages_count" : count_pending_messages(to_user=current_user, from_user=user)
        }

    response = {"status": True, "data": user_data}
    return HttpResponse(json.dumps(response))

