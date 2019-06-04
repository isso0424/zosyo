from django.db import models
from django.utils import timezone


class Registration(models.Model):
    book = models.CharField(max_length=100)
    user = models.CharField(max_length=20)
    day = models.CharField(max_length=20,default='なし')
    status = models.CharField(max_length=10)
    mail = models.CharField(max_length=30)
    who_want = models.CharField(max_length=20)


class Reservation(models.Model):
    wtr = models.CharField(max_length=30, null=True)
    who = models.CharField(max_length=20, null=True)
