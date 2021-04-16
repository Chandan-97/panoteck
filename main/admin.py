from django.contrib import admin
from main.models import Designation, UserProfile, OfficeLocation

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Designation)
admin.site.register(OfficeLocation)
