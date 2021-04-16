from django.db import models
from django.contrib.auth.models import User


class Designation(models.Model):
    name = models.TextField(max_length=50)
    slug = models.TextField(max_length=100)
    info = models.TextField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.name


class OfficeLocation(models.Model):
    loc = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="office_loc/", null=True, blank=True)

    def __str__(self):
        return self.loc


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")
    profile_pic = models.ImageField(
        upload_to="profilepics/", null=True, blank=True)
    location = models.TextField()
    timezone = models.TextField()
    designation = models.ForeignKey(
        Designation, on_delete=models.CASCADE, related_name="users", null=True, blank=True)
    is_online = models.BooleanField(default=False)
    office_loc = models.ForeignKey(OfficeLocation, on_delete=models.CASCADE, related_name="users",
                                   null=True, blank=True)

    def __str__(self):
        return self.user.username
