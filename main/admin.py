from django.contrib import admin
from main.models import Designation, UserProfile

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Designation)
