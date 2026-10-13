from django.db.models import Model
from django.db import models


class Program(Model):
    id = models.UUIDField(primary_key=True, null=False)
    text = models.TextField(max_length=500, null=False)
