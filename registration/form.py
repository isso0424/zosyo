from django import forms


class RegistFrom(forms.Form):
    mail = forms.CharField(
        label="メールアドレスを入力",
        required=True,
        widget=forms.TextInput(),
        max_length=100)
    user = forms.CharField(
        label="名前を入力",
        required=True,
        widget=forms.TextInput(),
        max_length=20)
    book = forms.CharField(
        label='借りる本の名前',
        required=True,
        widget=forms.TextInput(),
        max_length=100
    )


class ReturForm(forms.Form):
    book = forms.CharField(
        label='返す本の名前',
        required=True,
        widget=forms.TextInput(),
        max_length=100
    )


class Who_want(forms.Form):
    regist = forms.CharField(
        required=True,
        widget=forms.TextInput(),
        max_length=20
    )


class TourokuForm(forms.Form):
    book = forms.CharField(
        required=True,
        widget=forms.TextInput(),
        max_length=100,
        label='登録したい本の名前'
    )
