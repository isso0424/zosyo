from django.shortcuts import render, redirect
from .form import RegistFrom, ReturForm, Who_want, TourokuForm
from .models import Registration, Reservation
from django.utils import timezone


# Create your views here.


def index(request):
    if Reservation.objects.all().exists():
        Reservation.objects.all().delete()
    form = RegistFrom(request.POST or None)
    if form.is_valid():
        import datetime
        regist = Registration()
        day = timezone.datetime.today()
        regist.day = str(day).split(' ')[0]
        regist.book = form.cleaned_data.get('book')
        regist.user = form.cleaned_data.get('user')
        regist.mail = form.cleaned_data.get('mail')
        regist.status = "貸出中"
        regist.who_want = 'なし'
        print('get!')
        if Registration.objects.filter(book=regist.book, status='ラボ内').exists():
            if Registration.objects.filter(book=regist.book).exclude(who_want='なし').exists():
                regist.who_want = Registration.objects.filter(book=regist.book).values('who_want')[0]
                print(regist.who_want)
                print(regist.user)
                if regist.who_want['who_want'] == regist.user:
                    Registration.objects.filter(book=regist.book).delete()
                    Registration.objects.create(book=regist.book, user=regist.user, day=regist.day,
                                                status='貸出中', mail=regist.mail, who_want='なし')
                    return redirect('regist:regist')
                else:
                    d = {'form': form, 'error_reseva': True}
            else:
                regist.who_want = 'なし'
                Registration.objects.filter(book=regist.book).delete()
                Registration.objects.create(book=regist.book, user=regist.user, day=regist.day,
                                            status='貸出中', mail=regist.mail, who_want=regist.who_want)
                return redirect('regist:regist')
        else:
            if Registration.objects.filter(book=regist.book, status='貸出中', who_want='なし').exists():
                Reservation.objects.create(wtr=regist.book, who=regist.user)
                return redirect('regist:reservation')
            elif Registration.objects.filter(book=regist.book, status='貸出中').exists():
                d = {'form': form, 'error_resrva': True}
            else:
                d = {'form': form, 'error': True, }

    else:
        d = {'form': form, }
    return render(request, 'regist/regist.html', d)


def home(request):
    d = {'messages': Registration.objects.filter(status="貸出中"),
         'next': Registration.objects.exclude(who_want='なし')}
    return render(request, 'regist/home.html', d)


def retur(request):
    form = ReturForm(request.POST or None)
    if form.is_valid():
        regist = Registration()
        regist.book = form.cleaned_data.get('book')
        if Registration.objects.filter(book=regist.book).exists():
            if Registration.objects.filter(book=regist.book).exclude(who_want='なし').exists():
                regist.who_want = Registration.objects.filter(book=regist.book).values('who_want')[0]
                Registration.objects.filter(book=regist.book).delete()
                regist.mail = 'なし'
                regist.user = 'なし'
                regist.day = 0
                regist.status = "ラボ内"
                Registration.objects.create(book=regist.book, user=regist.user, day=regist.day,
                                            status=regist.status, mail=regist.mail, who_want=regist.who_want['who_want'])
            else:
                Registration.objects.filter(book=regist.book).delete()
                regist.mail = 'なし'
                regist.user = 'なし'
                regist.day = 0
                regist.status = "ラボ内"
                Registration.objects.create(book=regist.book, user=regist.user, day=regist.day,
                                            status=regist.status, mail=regist.mail, who_want='なし')
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
                day='なし',
                mail='なし',
                user='なし',
                who_want='なし'
            )
            return redirect('regist:touroku')
    return render(request, 'regist/touroku.html', {'form': form})


def reservation(request):
    form = Who_want(request.POST or None)
    wt = Reservation.objects.filter().values('wtr')[0]
    wh = Reservation.objects.filter().values('who')[0]
    if request.method == 'POST':
        if 'yes' in request.POST:
            print(wt)
            a = Registration.objects.filter(book=wt['wtr']).values()[0]
            Registration.objects.filter(book=wt['wtr']).delete()
            Registration.objects.create(
                book=wt['wtr'],
                status=a['status'],
                user=a['user'],
                mail=a['mail'],
                who_want=wh['who'],
                day=a['day'],
            )
            Reservation.objects.all().delete()
            return redirect('regist:home')
        elif 'no' in request.POST:
            return redirect('regist:home')
    d = {'reser_book': wt,
         'form': form,
         }
    return render(request, 'regist/reservation.html', d)
