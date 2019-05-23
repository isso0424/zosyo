from django.db import models
from django.utils import timezone


class Registration(models.Model):
    book = models.CharField(max_length=100)
    user = models.CharField(max_length=20)
    day = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10)
    mail = models.CharField(max_length=30)
    who_want = models.CharField(max_length=20)
