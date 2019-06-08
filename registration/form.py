from django import forms


# formをまとめてあるファイル
# 貸出登録form
class RegistFrom(forms.Form):
    # メアド用のform
    # charfieldは文字列を受け取るって意味
    mail = forms.CharField(
        # formについてるコメント
        label="メールアドレスを入力",
        # formが必須かどうか
        required=True,
        # テキストボックス
        widget=forms.TextInput(),
        # 最大の長さ
        max_length=100
    )
    # 1度説明したら割愛
    user = forms.CharField(
        label="名前を入力",
        required=True,
        widget=forms.TextInput(),
        max_length=20
    )
    book = forms.CharField(
        label='借りる本の名前',
        required=True,
        widget=forms.TextInput(),
        max_length=100
    )


# 蔵書検索form
class Book_searchForm(forms.Form):
    books_search = forms.CharField(
        label="蔵書検索欄",
        required=True,
        widget=forms.TextInput(),
        max_length=20
    )
    choice = forms.ChoiceField(
        label="検索方法選択",
        widget=forms.RadioSelect,
        choices=(
            (1, 'or'),
            (0, 'and'),
        ),
        initial=1,
        required=True
    )


# 返却用form
class ReturForm(forms.Form):
    book = forms.CharField(
        label='返す本の名前',
        required=True,
        widget=forms.TextInput(),
        max_length=100
    )


# 予約用form
class Who_want(forms.Form):
    regist = forms.CharField(
        required=True,
        widget=forms.TextInput(),
        max_length=20
    )


# 蔵書登録form
class TourokuForm(forms.Form):
    book = forms.CharField(
        required=True,
        widget=forms.TextInput(),
        max_length=100,
        label='登録したい本の名前'
    )
