from django.shortcuts import render, redirect
from .form import RegistFrom, ReturForm, Who_want, TourokuForm, Book_searchForm
from .models import Registration, Reservation, Search
from django.utils import timezone


# Create your views here.
########################################################
# dはhtmlに送る辞書
# 貸出登録ページのコントローラー
# ページを表示,またはsubmitされたときに関数を実行
def index(request):
    # 予約用のデータベースに値が残ってたら全部消す
    if Reservation.objects.all().exists():
        Reservation.objects.all().delete()
    # formが貸出フォーム
    form = RegistFrom(request.POST or None)
    # form2が蔵書検索フォーム
    form2 = Book_searchForm(request.POST or None)
    # formに値が入力されているか判定
    if form.is_valid():
        import datetime
        # さすがにデータベースをそのまま使うのはやばいと思ってregistとして定義
        regist = Registration()
        # dayは扱いがめんどいからstr型に変換
        day = timezone.datetime.today()
        regist.day = str(day).split(' ')[0]
        # book,user,mailはformに入力されている内容をform.cleaned_data.get('formの名前')で取得
        regist.book = form.cleaned_data.get('book')
        regist.user = form.cleaned_data.get('user')
        regist.mail = form.cleaned_data.get('mail')
        # 下２つはリセット用
        regist.status = "貸出中"
        # 入力された本のタイトルがデータベースにあり、借りられていないか判定
        if Registration.objects.filter(book=regist.book, status='ラボ内').exists():
            # 入力された本が予約されているか判定
            if Registration.objects.filter(book=regist.book).exclude(who_want='なし').exists():
                # who_wantに入力された本を予約している人を代入
                regist.who_want = Registration.objects.filter(book=regist.book).values('who_want')[0]
                # その代入された人が今回借りようとしてる人か判定
                if regist.who_want['who_want'] == regist.user:
                    # Trueならその本のデータベースを一回削除して予約者なしにして貸出
                    Registration.objects.filter(book=regist.book).delete()
                    Registration.objects.create(book=regist.book, user=regist.user, day=regist.day,
                                                status='貸出中', mail=regist.mail, who_want='なし')
                    # 貸出したら同じページにリダイレクトしてフォームをリセット
                    return redirect('regist:regist')
                # 別な人が借りようとしたらｶﾘﾚﾅｲﾖ-ってことを出力
                else:
                    d = {'form': form, 'error_reseva': True, 'form2': form2}
            # 予約されてなければそのまま借りる
            else:
                regist.who_want = 'なし'
                # 本のデータベースを一回削除して貸出
                Registration.objects.filter(book=regist.book).delete()
                Registration.objects.create(book=regist.book, user=regist.user, day=regist.day,
                                            status='貸出中', mail=regist.mail, who_want=regist.who_want)
                # 貸出したら同じページにリダイレクトしてフォームをリセット
                return redirect('regist:regist')
        # 本が貸出中で予約なしなら予約の催促をする
        elif Registration.objects.filter(book=regist.book, status='貸出中', who_want='なし').exists():
            Reservation.objects.create(wtr=regist.book, who=regist.user)
            # 予約確認ページに飛ぶ
            return redirect('regist:reservation')
        # 予約されてるならそのことを出力
        elif Registration.objects.filter(book=regist.book, status='貸出中').exists():
            d = {'form': form, 'error_resrva': True, 'form2': form2}
        # ここまで来たら本がないってエラー出す
        else:
            d = {'form': form, 'error': True, 'form2': form2}
    # 検索用フォームに値が入力されているかを判定
    if form2.is_valid():
        # 入力された本を.cleaned_data.get('books_search')してbooks_searchに挿入
        search_books = form2.cleaned_data.get('books_search')
        # 変数を初期化
        ok = False
        # もし検索履歴が残ってたら削除
        if Search.objects.all().exists():
            Search.objects.all().delete()
        # データベースのすべての本をfor文で総当たりして{'book':本の名前}の形の辞書をbool_dateに代入
        for book_date in Registration.objects.all().values('book'):
            # {'book': 本の名前}の本の名前をbook_listsに代入
            for book_lists in book_date.values():
                # book_listsの本に検索ワードが含まれているか判定
                if search_books in book_lists:
                    # 検索ワードが含まれていた場合Search(データベース)に本の名前をぶち込む
                    Search.objects.create(
                        search_book=book_lists,
                    )
                    # okをTrueにすることで次のif文でdの形を検索結果付きに変更
                    ok = True
        if ok:
            # searchにTrueを送り、htmlのif文に利用,search_resultにすべての検索結果をぶち込む
            d = {'form': form, 'form2': form2, 'search': True, 'search_result': Search.objects.all()}
        # 検索ワードに対応するものがなければその旨をsearch_errorでhtmlに反映
        else:
            d = {'form': form, 'form2': form2, 'search_error': True}
    # ページ読み込み時に表示するもの
    else:
        d = {'form': form, 'form2': form2}
    # htmlにdをぶちこんでhtmlを操作
    return render(request, 'regist/regist.html', d)


def home(request):
    # 'messages'に貸出中の本を,'next'に予約されている本の一覧を表示
    d = {'messages': Registration.objects.filter(status="貸出中"),
         'next': Registration.objects.exclude(who_want='なし')}
    # indexといっしょ
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
