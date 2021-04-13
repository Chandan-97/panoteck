from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Room(models.Model):
    """Represents chat rooms that users can join"""
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    slug = models.CharField(max_length=50)

    def __str__(self):
        """Returns human-readable representation of the model instance."""
        return self.name


class Message(models.Model):
    SENT = 'SENT'
    RECEIVED = 'RECEIVED'
    PENDING = 'PENDING'

    from_user = models.ForeignKey(User)
    to_user = models.ForeignKey(User)
    body = models.TextField(max_length=1000, null=True, blank=True)
    status = models.TextField(max_length=20, default=SENT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body
