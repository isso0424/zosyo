from django.shortcuts import render,get_object_or_404,redirect
from .form import RegistFrom
from .models import Regist
from django import forms
from . import form
import datetime
from django.utils import timezone
# Create your views here.
def index(request):
    form = RegistFrom(request.POST or None)
    if form.is_valid():
        regist = Regist()
        regist.day = timezone.datetime.today()
        regist.book = form.cleaned_data.get('book')
        regist.mail = form.cleaned_data.get('mail')
        regist.user = form.cleaned_data.get('user')
        print('get!')
        Regist.objects.create(
            book=regist.book,
            mail=regist.mail,
            user=regist.user,
            day=regist.day
        )
        return redirect('regist:regist')
    return render(request, 'regist/regist.html', {'form': form})
def home(request):
    d = {
        'messages':Regist.objects.all()
    }
    return render(request, 'regist/home.html',d)