from django.shortcuts import render, redirect
from .form import RegistFrom, ReturForm, Who_Want, TourokuForm, \
    Books_SearchForm, SignUpForm, RegistFrom_bot, ReturForm_bot
from .models import Registration, Reservation, Search
from django.utils import timezone
from django.contrib.auth.models import User
import datetime


# Create your views here.
########################################################
# dはhtmlに送る辞書                                    #
# formはforms.pyを参照                                 #
# データベースはmodels.pyを参照                        #
# ページを表示,またはsubmitされたときに関数を実行      #
########################################################
# 貸出登録ページのコントローラー
def index(request):
    if request.user.is_authenticated:
        username = str(request.user)
    else:
        return render(request, 'regist/non_login.html', {
            'messages': Registration.objects.filter(status="貸出中"),
            'next': Registration.objects.exclude(who_want='なし'),
            'user': None})
    # 予約用のデータベースに値が残ってたら全部消す
    if Reservation.objects.all().exists():
        Reservation.objects.all().delete()
    # formが貸出フォーム
    form = RegistFrom(request.POST or None)
    # search_formが蔵書検索フォーム
    search_form = Books_SearchForm(request.POST or None)
    # formに値が入力されているか判定
    if form.is_valid():
        # さすがにデータベースをそのまま使うのはやばいと思ってregistとして定義
        regist = Registration()
        # dayは扱いがめんどいからstr型に変換
        day = timezone.datetime.today()
        regist.day = str(day).split(' ')[0]
        # book,user,mailはformに入力されている内容をform.cleaned_data.get('formの名前')で取得
        regist.book = form.cleaned_data.get('book')
        regist.user = username
        regist.mail = request.user.email
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
                    d = {'form': form, 'error_reseva': True, 'search_form': search_form, 'user': username}
            # 予約されてなければそのまま借りる
            else:
                regist.who_want = 'なし'
                # 本のデータベースを一回削除して貸出
                Registration.objects.filter(book=regist.book).delete()
                Registration.objects.create(
                    book     = regist.book,
                    user     = regist.user,
                    day      = regist.day,
                    status   = '貸出中',
                    mail     = regist.mail,
                    who_want = regist.who_want
                )
                # 貸出したら同じページにリダイレクトしてフォームをリセット
                return redirect('regist:regist')
        # 本が貸出中で予約なしなら予約の催促をする
        elif Registration.objects.filter(
                book    = regist.book,
                status  = '貸出中',
                who_want= 'なし'
        ).exists():
            # 本とユーザー名を予約用のデータベースに登録する
            Reservation.objects.create(
                wtr = regist.book,
                who = regist.user
            )
            # 予約確認ページに飛ぶ
            return redirect('regist:reservation')
        # 予約されてるならそのことを出力
        elif Registration.objects.filter(book=regist.book, status='貸出中').exists():
            d = {
                'form': form,
                'error_resrva': True,
                'search_form': search_form,
                'user': username
            }
        # ここまで来たら本がないってエラー出す
        else:
            d = {
                'form': form,
                'error': True,
                'search_form': search_form,
                'user': username
            }
    # 検索用フォームに値が入力されているかを判定
    elif search_form.is_valid():
        # 入力された本を.cleaned_data.get('books_search')してbooks_searchに挿入
        search_books = search_form.cleaned_data.get('books_search')
        # 検索ワードをリスト化
        search_words = search_books.split()
        # 変数を初期化
        ok = False
        # もし検索履歴が残ってたら削除
        if Search.objects.all().exists():
            Search.objects.all().delete()
        # データベースのすべての本をfor文で総当たりして{'book':本の名前}の形の辞書をbool_dateに代入
        for book_date in Registration.objects.all().values('book'):
            # {'book': 本の名前}の本の名前をbook_listsに代入
            for book_lists in book_date.values():
                # book_listsの本に検索ワードの1番目が含まれているか判定
                if search_words[0] in book_lists:
                    # 検索ワードが含まれていた場合Search(データベース)に本の名前をぶち込む
                    Search.objects.create(
                        search_book=book_lists,
                    )
                    # okをTrueにすることで次のif文でdの形を検索結果付きに変更
                    ok = True
        # さっき検索したワードは削除する
        del search_words[0]
        choice = search_form.cleaned_data['choice']
        # 残ったワードにさっきやった処理をかけていく
        a = False

        # and検索の場合
        if choice == "0":
            for search in search_words:
                a = True
                for book_date in Search.objects.all().values('search_book'):
                    for book_lists in book_date.values():
                        # book_listsの本に検索ワードのn番目が含まれているか判定
                        if search in book_lists:
                            # 検索ワードが含まれていた場合pass
                            pass
                        else:
                            # 含まれていない本は除外
                            Search.objects.filter(search_book=book_lists).delete()

        # or検索の場合
        if choice == "1":
            for search_b in search_words:
                for book_date in Registration.objects.all().values('book'):
                    # {'book': 本の名前}の本の名前をbook_listsに代入
                    for book_lists in book_date.values():
                        # book_listsの本に検索ワードの1番目が含まれているか判定
                        if search_b in book_lists:
                            # 検索ワードが含まれていた場合Search(データベース)に本の名前をぶち込む
                            if Search.objects.filter(search_book=book_lists):
                                pass
                            else:
                                Search.objects.create(
                                    search_book=book_lists,
                                )
                            # okをTrueにすることで次のif文でdの形を検索結果付きに変更
                            ok = True
        if a:
            if not Search.objects.all().exists():
                ok = False
        if ok:
            # searchにTrueを送り、htmlのif文に利用,search_resultにすべての検索結果をぶち込む
            d = {'form': form, 'search_form': search_form, 'search': True, 'search_result': Search.objects.all(), 'user': username}
        # 検索ワードに対応するものがなければその旨をsearch_errorでhtmlに反映
        else:
            d = {'form': form, 'search_form': search_form, 'search_error': True, 'user': username}
    # ページ読み込み時に表示するもの
    else:
        d = {'form': form, 'search_form': search_form, 'user': username}
    # htmlにdをぶちこんでhtmlを操作
    return render(request, 'regist/regist.html', d)


# トップページのコントローラー
def home(request):
    if request.user.is_authenticated:
        username = str(request.user)
        print(User.objects.all().values('email'))
    else:
        return render(
            request,
            'regist/home.html',
            {
                'messages': Registration.objects.filter(status="貸出中"),
                'next': Registration.objects.exclude(who_want='なし'),
                'user': None
            }
        )
    # 'messages'に貸出中の本を,'next'に予約されている本の一覧を表示
    d = {
        'messages': Registration.objects.filter(status="貸出中"),
        'next': Registration.objects.exclude(who_want='なし'),
        'user': username
    }
    # indexといっしょ
    return render(request, 'regist/home.html', d)


# 返却ページのコントローラ－
def retur(request):
    if request.user.is_authenticated:
        username = str(request.user)
    else:
        return render(
            request,
            'regist/non_login.html',
            {
                'messages': Registration.objects.filter(status="貸出中"),
                'next': Registration.objects.exclude(who_want='なし'),
                'user': None
            }
        )
    # formは返却用のReturFormを使用
    form = ReturForm(request.POST or None)

    # formに値が入力されていたらTrue
    if form.is_valid():
        # どのデータベースに代入するかわかりやすいようにregistにRegistrationを代入
        regist = Registration()
        # ('book')にform.cleaned_date.getで本を代入
        regist.book = form.cleaned_data.get('book')
        if Registration.objects.filter(book=regist.book).exists():
            # 予約されてる場合、その人を
            if Registration.objects.filter(book=regist.book).exclude(who_want='なし').exists():
                regist.who_want = Registration.objects.filter(book=regist.book).values('who_want')[0]
                Registration.objects.filter(book=regist.book).delete()
                Registration.objects.create(
                    book     = regist.book,
                    user     = 'なし',
                    day      = 'なし',
                    status   = 'ラボ内',
                    mail     = 'なし',
                    who_want = regist.who_want['who_want']
                )
            # 予約されてない場合の操作
            else:
                # その本のデータベースの削除
                Registration.objects.filter(book=regist.book).delete()
                # データベースの作り直し
                Registration.objects.create(
                    book     = regist.book,
                    user     = 'なし',
                    day      = 'なし',
                    status   = 'ラボ内',
                    mail     = 'なし',
                    who_want = 'なし'
                )
            # どっちにせよ返却したあとリダイレクトしてフォームをリセット
            return redirect('regist:retur')
        else:
            d = {
                'form': form,
                'error': True,
                "user": username,
                'borrow': True
            }
    elif Registration.objects.filter(user=username).exists():
        d = {
            'form': form,
            'user': username,
            'borrow': True,
            'borrowing': Registration.objects.filter(user=username)
        }
    else:
        d = {
            'form': form,
            "user": username
        }
    # おまじない
    return render(
        request,
        'regist/retur.html',
        d
    )


# 蔵書一覧の関数
def book_list(request):
    if request.user.is_authenticated:
        username = str(request.user)
        # ラボ内にある本をIn_labとしてhtmlで使用
        d = {'In_lab': Registration.objects.filter(status="ラボ内", who_want='なし'),
             'can_reser': Registration.objects.filter(status="貸出中", who_want='なし'), "user": username}
    else:
        d = {'In_lab': Registration.objects.filter(status="ラボ内", who_want='なし'),
             'can_reser': Registration.objects.filter(status="貸出中", who_want='なし')}
    # おまじない
    return render(request, 'regist/book_list.html', d)


# 蔵書登録ページ
def touroku(request):
    if request.user.is_authenticated:
        username = str(request.user)
    else:
        return render(
            request,
            'regist/non_login.html',
            {
                'messages': Registration.objects.filter(status="貸出中"),
                'next':     Registration.objects.exclude(who_want='なし'),
                'user':     None
            }
        )
    # formは登録用のTourokuFormを使用
    form = TourokuForm(request.POST or None)
    # formが値で埋まっていれば登録を行う
    if form.is_valid():
        regist = Registration()
        regist.book = form.cleaned_data.get('book')
        # 本がデータベースに無い場合、本を追加する
        if not Registration.objects.filter(book=regist.book).exists():
            Registration.objects.create(
                book     = regist.book,
                status   = 'ラボ内',
                day      = 'なし',
                mail     = 'なし',
                user     = 'なし',
                who_want = 'なし'
            )
            return redirect('regist:touroku')
        else:
            d = {'form': form, 'error': True, "user": username}
    else:
        d = {'form': form, "user": username}
    return render(request, 'regist/touroku.html', d)


# 予約催促用
def reservation(request):
    if request.user.is_authenticated:
        username = str(request.user)
    else:
        return render(
            request,
            'regist/non_login.html',
            {
                'messages': Registration.objects.filter(status="貸出中"),
                'next':     Registration.objects.exclude(who_want='なし'),
                'user':     None
            }
        )
    # formは予約ページのフォームのWho_wantを使用
    form = Who_Want(request.POST or None)
    # indexの予約の分岐でぶち込まれたユーザー名と予約する本を変数にぶち込む
    wt = Reservation.objects.filter().values('wtr')[0]
    wh = Reservation.objects.filter().values('who')[0]
    # submitボタンを押した際に分岐
    if request.method == 'POST':
        # yesボタンを押したとき
        if 'yes' in request.POST:
            # aに予約する本のRegistrationデータベースの辞書を代入
            a = Registration.objects.filter(book=wt['wtr']).values()[0]
            # 上で代入したもとのデータベースを削除
            Registration.objects.filter(book=wt['wtr']).delete()
            # 代わりにwho_wantが代入されたデータベースをcreate
            Registration.objects.create(
                book     = wt['wtr'],
                status   = a['status'],
                user     = a['user'],
                mail     = a['mail'],
                who_want = wh['who'],
                day      = a['day'],
            )
            # 予約用データベースの削除
            Reservation.objects.all().delete()
            # ホームに戻る
            return redirect('regist:home')
        # noボタンを押したとき
        elif 'no' in request.POST:
            # 何もせずにホームに戻る
            return redirect('regist:home')
    # dに予約する本とformをぶちこむ
    d = {
        'reser_book': wt,
        'form': form,
        "user": username
    }
    return render(
        request,
        'regist/reservation.html',
        d
    )


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('regist:home')
    else:
        form = SignUpForm()
    context = {
        'form': form
    }
    return render(
        request,
        'regist/signup.html',
        context
    )


def setting(request):
    if request.user.is_authenticated:
        username = str(request.user)
        d = {
            'user': username
        }
        return render(
            request,
            'regist/setting.html',
            d
        )
    else:
        return redirect('regist:non_login.html')


def for_bot(request):
    # 予約用のデータベースに値が残ってたら全部消す
    if Reservation.objects.all().exists():
        Reservation.objects.all().delete()
    # formが貸出フォーム
    form = RegistFrom_bot(request.POST or None)

    # formに値が入力されているか判定
    if form.is_valid():
        # さすがにデータベースをそのまま使うのはやばいと思ってregistとして定義
        regist = Registration()
        # dayは扱いがめんどいからstr型に変換
        day = timezone.datetime.today()
        regist.day = str(day).split(' ')[0]

        # book,user,mailはformに入力されている内容をform.cleaned_data.get('formの名前')で取得
        regist.book = form.cleaned_data.get('book')
        regist.user = form.cleaned_data.get('user')
        if not User.objects.filter(username=regist.user).exists():
            return redirect('regist:home')

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
                    Registration.objects.create(
                        book=regist.book,
                        user=regist.user,
                        day=regist.day,
                        status='貸出中',
                        mail='discord',
                        who_want='なし'
                    )
                    # 貸出したら同じページにリダイレクトしてフォームをリセット
                    return redirect('regist:bot')
                # 別な人が借りようとしたらｶﾘﾚﾅｲﾖ-ってことを出力
                else:
                    return redirect('regist:book_list')
            # 予約されてなければそのまま借りる
            else:
                regist.who_want = 'なし'
                # 本のデータベースを一回削除して貸出
                Registration.objects.filter(book=regist.book).delete()
                Registration.objects.create(book=regist.book, user=regist.user, day=regist.day,
                                            status='貸出中', mail='discord', who_want=regist.who_want)
                # 貸出したら同じページにリダイレクトしてフォームをリセット
                return redirect('regist:bot')
        # 本が貸出中で予約なしなら予約の催促をする
        elif Registration.objects.filter(book=regist.book, status='貸出中', who_want='なし').exists():
            # 本とユーザー名を予約用のデータベースに登録する
            Reservation.objects.create(wtr=regist.book, who=regist.user)
            # 予約確認ページに飛ぶ
            return redirect('regist:reservation')
        # 予約されてるならそのことを出力
        elif Registration.objects.filter(book=regist.book, status='貸出中').exists():
            return redirect('regist:book_list')
        # ここまで来たら本がないってエラー出す
        else:
            return redirect('regist:retur')
    # ページ読み込み時に表示するもの
    else:
        d = {'form': form}
    # htmlにdをぶちこんでhtmlを操作
    return render(request, 'regist/regist_bot.html', d)


# 返却ページのコントローラ－
def bot_return(request):
    # formは返却用のReturFormを使用
    form = ReturForm_bot(request.POST or None)
    # formに値が入力されていたらTrue
    if form.is_valid():
        # どのデータベースに代入するかわかりやすいようにregistにRegistrationを代入
        regist = Registration()
        # ('book')にform.cleaned_date.getで本を代入
        regist.book = form.cleaned_data.get('book')
        regist.user = form.cleaned_data.get('user')
        # 入力された本があるかどうか判定
        if Registration.objects.filter(book=regist.book, user=regist.user).exists():
            # 以下の4つは初期化用
            regist.mail = 'なし'
            regist.user = 'なし'
            regist.day = 'なし'
            regist.status = "ラボ内"
            # 予約されてるか判定
            if Registration.objects.filter(book=regist.book).exclude(who_want='なし').exists():
                # 予約してる人を取得
                regist.who_want = Registration.objects.filter(book=regist.book).values('who_want')[0]
                # その本のデータベースの削除
                Registration.objects.filter(book=regist.book).delete()
                # データベースの作り直し
                Registration.objects.create(book=regist.book, user=regist.user, day=regist.day,
                                            status=regist.status, mail=regist.mail,
                                            who_want=regist.who_want['who_want'])
            # 予約されてない場合の操作
            else:
                # その本のデータベースの削除
                Registration.objects.filter(book=regist.book).delete()
                # データベースの作り直し
                Registration.objects.create(book=regist.book, user=regist.user, day=regist.day,
                                            status=regist.status, mail=regist.mail, who_want='なし')
            # どっちにせよ返却したあとリダイレクトしてフォームをリセット
            return redirect('regist:rebot')
        else:
            return redirect('regist:home')
    else:
        d = {'form': form}
    # おまじない
    return render(request, 'regist/rebot.html', d)


def bot_page(request):
    if "command" in request.GET and "user" in request.GET and "book" in request.GET:
        command = request.GET.get("command")
        user = request.GET.get("user")
        book = request.GET.get("book")
        if command == "borrow":
            return bot_borrow(book, user)
        elif command == "return":
            return bot_return(book, user)

    return render(request, 'regist/bot.html', {})

def bot_borrow(book, user):
    # 予約用のデータベースに値が残ってたら全部消す
    if Reservation.objects.all().exists():
        Reservation.objects.all().delete()
    # さすがにデータベースをそのまま使うのはやばいと思ってregistとして定義
    regist = Registration()
    # dayは扱いがめんどいからstr型に変換
    day = timezone.datetime.today()
    regist.day = str(day).split(' ')[0]

    # book,user,mailはformに入力されている内容をform.cleaned_data.get('formの名前')で取得
    if not User.objects.filter(username=user).exists():
        return redirect('regist:home')

    # 下２つはリセット用
    regist.status = "貸出中"
    # 入力された本のタイトルがデータベースにあり、借りられていないか判定
    if Registration.objects.filter(book=book, status='ラボ内').exists():
        # 入力された本が予約されているか判定
        if Registration.objects.filter(book=book).exclude(who_want='なし').exists():
            # who_wantに入力された本を予約している人を代入
            regist.who_want = Registration.objects.filter(book=book).values('who_want')[0]
            # その代入された人が今回借りようとしてる人か判定
            if regist.who_want['who_want'] == user:
                # Trueならその本のデータベースを一回削除して予約者なしにして貸出
                Registration.objects.filter(book=book).delete()
                Registration.objects.create(
                    book=book,
                    user=user,
                    day=regist.day,
                    status='貸出中',
                    mail='discord',
                    who_want='なし'
                )
                # 貸出したら同じページにリダイレクトしてフォームをリセット
                return redirect('regist:bot')
            # 別な人が借りようとしたらｶﾘﾚﾅｲﾖ-ってことを出力
            else:
                return redirect('regist:book_list')
        # 予約されてなければそのまま借りる
        else:
            regist.who_want = 'なし'
            # 本のデータベースを一回削除して貸出
            Registration.objects.filter(book=book).delete()
            Registration.objects.create(
                book=book, 
                user=user, 
                day=regist.day,
                status='貸出中', 
                mail='discord', 
                who_want=regist.who_want
            )
            # 貸出したら同じページにリダイレクトしてフォームをリセット
            return redirect('regist:bot')
    # ここまで来たら本がないってエラー出す
    else:
        return redirect('regist:retur')
    # htmlにdをぶちこんでhtmlを操作

def bot_return(book, user):
    # どのデータベースに代入するかわかりやすいようにregistにRegistrationを代入
    regist = Registration()
    # ('book')にform.cleaned_date.getで本を代入
    regist.book = book
    regist.user = user
    # 入力された本があるかどうか判定
    if Registration.objects.filter(book=regist.book, user=regist.user).exists():
        # 以下の4つは初期化用
        regist.mail = 'なし'
        regist.user = 'なし'
        regist.day = 'なし'
        regist.status = "ラボ内"
        # 予約されてるか判定
        if Registration.objects.filter(book=regist.book).exclude(who_want='なし').exists():
            # 予約してる人を取得
            regist.who_want = Registration.objects.filter(book=regist.book).values('who_want')[0]
            # その本のデータベースの削除
            Registration.objects.filter(book=regist.book).delete()
            # データベースの作り直し
            Registration.objects.create(book=regist.book, user=regist.user, day=regist.day,
                                        status=regist.status, mail=regist.mail,
                                        who_want=regist.who_want['who_want'])
        # 予約されてない場合の操作
        else:
            # その本のデータベースの削除
            Registration.objects.filter(book=regist.book).delete()
            # データベースの作り直し
            Registration.objects.create(book=regist.book, user=regist.user, day=regist.day,
                                        status=regist.status, mail=regist.mail, who_want='なし')
        # どっちにせよ返却したあとリダイレクトしてフォームをリセット
        return redirect('regist:home')
    return redirect('regist:home')
