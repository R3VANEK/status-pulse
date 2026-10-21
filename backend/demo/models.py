from django.db.models import Model
from django.db import models


class Users(Model):
    id = models.BigIntegerField(primary_key=True, null=False)
    email = models.EmailField(default="foo@example.com")


class Program(Model):
    id = models.UUIDField(primary_key=True, null=False)
    text = models.TextField(max_length=500, null=False)
    user = models.ForeignKey(to=Users, on_delete=models.CASCADE, null=True)
