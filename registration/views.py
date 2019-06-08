from django.shortcuts import render, redirect
from .form import RegistFrom, ReturForm, Who_want, TourokuForm, Book_searchForm
from .models import Registration, Reservation, Search
from django.utils import timezone


# Create your views here.
########################################################
# dはhtmlに送る辞書                                    #
# formはforms.pyを参照                                 #
# データベースはmodels.pyを参照                        #
# ページを表示,またはsubmitされたときに関数を実行      #
########################################################
# 貸出登録ページのコントローラー
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
            # 本とユーザー名を予約用のデータベースに登録する
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
        choice = form2.cleaned_data['choice']
        print(choice)
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
        print(search_words)
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
            d = {'form': form, 'form2': form2, 'search': True, 'search_result': Search.objects.all()}
        # 検索ワードに対応するものがなければその旨をsearch_errorでhtmlに反映
        else:
            d = {'form': form, 'form2': form2, 'search_error': True}
    # ページ読み込み時に表示するもの
    else:
        d = {'form': form, 'form2': form2}
    # htmlにdをぶちこんでhtmlを操作
    return render(request, 'regist/regist.html', d)


# トップページのコントローラー
def home(request):
    # 'messages'に貸出中の本を,'next'に予約されている本の一覧を表示
    d = {'messages': Registration.objects.filter(status="貸出中"),
         'next': Registration.objects.exclude(who_want='なし')}
    # indexといっしょ
    return render(request, 'regist/home.html', d)


# 返却ページのコントローラ－
def retur(request):
    # formは返却用のReturFormを使用
    form = ReturForm(request.POST or None)
    # formに値が入力されていたらTrue
    if form.is_valid():
        # どのデータベースに代入するかわかりやすいようにregistにRegistrationを代入
        regist = Registration()
        # ('book')にform.cleaned_date.getで本を代入
        regist.book = form.cleaned_data.get('book')
        # 入力された本があるかどうか判定
        if Registration.objects.filter(book=regist.book).exists():
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
                                            status=regist.status, mail=regist.mail, who_want=regist.who_want['who_want'])
            # 予約されてない場合の操作
            else:
                # その本のデータベースの削除
                Registration.objects.filter(book=regist.book).delete()
                # データベースの作り直し
                Registration.objects.create(book=regist.book, user=regist.user, day=regist.day,
                                            status=regist.status, mail=regist.mail, who_want='なし')
            # どっちにせよ返却したあとリダイレクトしてフォームをリセット
            return redirect('regist:retur')
    # おまじない
    return render(request, 'regist/retur.html', {'form': form})


# 蔵書一覧の関数
def book_list(request):
    # ラボ内にある本をIn_labとしてhtmlで使用
    d = {'In_lab': Registration.objects.filter(status="ラボ内")}
    # おまじない
    return render(request, 'regist/book_list.html', d)


# 蔵書登録ページ
def touroku(request):
    # formは登録用のTourokuFormを使用
    form = TourokuForm(request.POST or None)
    # フォームが埋まってるときにsubmitされたらTrue
    if form.is_valid():
        # 上の方からずっとやってるおまじない
        regist = Registration()
        # おまじない
        regist.book = form.cleaned_data.get('book')
        # 本がデータベースになければ分岐
        if not Registration.objects.filter(book=regist.book).exists():
            # いつもどおりにcreate
            # それぞれのステータスは初期化されたものを使う
            Registration.objects.create(
                book=regist.book,
                status='ラボ内',
                day='なし',
                mail='なし',
                user='なし',
                who_want='なし'
            )
            return redirect('regist:touroku')
    return render(request, 'regist/touroku.html', {'form': form})


# 予約催促用
def reservation(request):
    # formは予約ページのフォームのWho_wantを使用
    form = Who_want(request.POST or None)
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
            # wt['wtr`]の意味がわからなかったら辞書について学び直せ
            Registration.objects.create(
                book=wt['wtr'],
                status=a['status'],
                user=a['user'],
                mail=a['mail'],
                who_want=wh['who'],
                day=a['day'],
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
    d = {'reser_book': wt,
         'form': form,
         }
    # おまじない
    return render(request, 'regist/reservation.html', d)
