from django.db import models
from django.contrib.auth.models import User


class Designation(models.Model):
    name = models.TextField(max_length=50)
    slug = models.TextField(max_length=100)
    info = models.TextField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.user.username
