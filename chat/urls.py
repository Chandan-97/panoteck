from django.contrib import admin
from django.urls import path
from .views import all_rooms, room_detail, token

urlpatterns = [
    path('', all_rooms, name='all_rooms'),
    path('rooms/<slug>/', room_detail, name="room_detail"),
    path('token/', token, name="token")
]
