from django.contrib import admin
from django.urls import path
from main.views import Login, Logout, CurrentUser

urlpatterns = [
    path('login/', Login, name='login'),
    path('logout/', Logout, name='logout'),
    path('user/', CurrentUser, name='current_user')
]
