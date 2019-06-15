from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput, label="ユーザー名")
    password = forms.CharField(widget=forms.PasswordInput, label="パスワード")


class SignUpForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput, label="ユーザー名")
    enter_password = forms.CharField(widget=forms.PasswordInput, label="パスワード")
    retype_password = forms.CharField(widget=forms.PasswordInput, label="パスワード(再入力)")
    email = forms.EmailField(label="メールアドレス")

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('そのユーザー名は既に使用されています')
        return username

    def clean_enter_password(self):
        password = self.cleaned_data.get('enter_password')
        if len(password) < 5:
            raise forms.ValidationError('パスワードは5文字以上です')
        return password

    def e_mail(self):
        e_mail = self.cleaned_data.get('email')
        if User.objects.filter(email=e_mail).exists():
            raise forms.ValidationError('そのメールアドレスは既に使用されています')

    def clean(self):
        super(SignUpForm, self).clean()
        password = self.cleaned_data.get('enter_password')
        retyped = self.cleaned_data.get('retype_password')
        if password and retyped and (password != retyped):
            self.add_error('retype_password', 'パスワードが一致しませんでした')

    def save(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('enter_password')
        e_mail = self.cleaned_data.get('email')
        new_user = User.objects.create_user(username=username, email=e_mail)
        new_user.set_password(password)
        new_user.save()


# formをまとめてあるファイル
# 貸出登録form
class RegistFrom(forms.Form):
    # メアド用のform
    # charfieldは文字列を受け取るって意味
    book = forms.CharField(
        label='借りる本の名前',
        required=True,
        widget=forms.TextInput(),
        max_length=100
    )


# 蔵書検索form
class Books_SearchForm(forms.Form):
    books_search = forms.CharField(
        label="蔵書検索欄",
        required=True,
        widget=forms.TextInput(),
        max_length=100
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
class Who_Want(forms.Form):
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
