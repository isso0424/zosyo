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