from allauth.account.adapter import DefaultAccountAdapter


class MyAccountAdapter(DefaultAccountAdapter):
    def __init__(self):
        super().__init__(self, request=None)
    def get_login_redirect_url(self, request):
        return 'https://isso4129.pythonanywhere.com/registration/home'