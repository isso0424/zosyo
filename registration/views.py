from django.shortcuts import render, redirect
from .form import RegistFrom, ReturForm, Who_want, TourokuForm
from .models import Registration
from django.utils import timezone


# Create your views here.


def index(request):
    form = RegistFrom(request.POST or None)
    if form.is_valid():
        import datetime
        regist = Registration()
        regist.day = timezone.datetime.today()
        regist.book = form.cleaned_data.get('book')
        regist.user = form.cleaned_data.get('user')
        regist.mail = form.cleaned_data.get('mail')
        regist.status = "貸出中"
        regist.who_want = 'なし'
        print('get!')
        r = Registration.objects.filter(status='ラボ内', book=regist.book).exists()
        print(r)
        if Registration.objects.filter(status='ラボ内').exists():
            if Registration.objects.filter(book=regist.book).exists():
                Registration.objects.filter(book=regist.book).delete()
                Registration.objects.create(book=regist.book, user=regist.user, day=regist.day,
                                            status='貸出中', mail=regist.mail, who_want=regist.who_want)
                return redirect('regist:regist')
            else:
                d = {'form': form, 'error': True, }
        else:
            d = {'form': form, 'error': True, }

    else:
        d = {'form': form, }
    return render(request, 'regist/regist.html', d)


def home(request):
    form = Who_want(request.POST or None)
    if form.is_valid():
        regist = Registration()
        regist.who_want = form.cleaned_data.get('regist')
        Registration.objects.add(who_want=regist.who_want, )
        return redirect('regist:home')
    d = {'messages': Registration.objects.filter(status="貸出中"), 'form': form, }
    return render(request, 'regist/home.html', d)


def retur(request):
    form = ReturForm(request.POST or None)
    if form.is_valid():
        regist = Registration()
        regist.book = form.cleaned_data.get('book')
        Registration.objects.filter(book=regist.book).delete()
        regist.mail = 'なし'
        regist.user = 'なし'
        regist.day = None
        regist.status = "ラボ内"
        Registration.objects.create(book=regist.book, user=regist.user, day=None,
                                    status=regist.status, mail=regist.mail)
        return redirect('regist:retur')
    return render(request, 'regist/retur.html', {'form': form})


def book_list(request):
    d = {'In_lab': Registration.objects.filter(status="ラボ内")}
    return render(request, 'regist/book_list.html', d)


def touroku(request):
    form = TourokuForm(request.POST or None)
    if form.is_valid():
        regist = Registration()
        regist.book = form.cleaned_data.get('book')
        regist.status = 'ラボ内'
        if not Registration.objects.filter(book=regist.book).exists():
            Registration.objects.create(
                book=regist.book,
                status=regist.status,
                day=None,
                mail='なし',
                user='なし',
                who_want='なし'
            )
            return redirect('regist:touroku')
    return render(request, 'regist/touroku.html', {'form': form})
