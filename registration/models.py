from django.db import models
from django.contrib.admin import widgets
from django import forms
from .form import RegistFrom
from django.utils import timezone


class Regist(models.Model):
    book = models.CharField(max_length=100)
    mail = models.CharField(max_length=100)
    user = models.CharField(max_length=20)
    day = models.DateTimeField(default=timezone.now)
class Retur(models.Model):
    bo = models.CharField(max_length=50)
    us = models.CharField(max_length=50)