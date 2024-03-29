from django.urls import path
from .views import all_rooms, room_detail, token, chat_users, user, \
    send_message, receive_message, poll_new_messages, poll_data, list_location, \
    set_location

urlpatterns = [
    path('', all_rooms, name='all_rooms'),
    path('rooms/<slug>/', room_detail, name="room_detail"),
    path('token/', token, name="token"),
    path('chat_users/', chat_users, name="chat_users_list"),
    path('user/', user, name="user_detail"),
    path('send/', send_message, name="send_message"),
    path('receive/', receive_message, name="receive_message"),
    path('poll_new_messages/', poll_new_messages, name="poll_message"),
    path('poll_data/', poll_data, name="poll_data"),
    path('list_office_loc/', list_location, name="list_location"),
    path('set_location/', set_location, name="set_location")
]
