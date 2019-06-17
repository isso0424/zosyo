from allauth.account.adapter import DefaultAccountAdapter


class MyAccountAdapter(DefaultAccountAdapter):
    def __init__(self):
        super().__init__(self, request=None)
    def get_login_redirect_url(self, request):
        return 'http://127.0.0.1:8000/'