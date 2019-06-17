from django.conf.urls import url
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
# アプリ名を定義
app_name = "regist"
# urlの定義
urlpatterns = (
    # 貸出用ページのurl
    url(r'^regist', views.index, name='regist'),
    # ホームのurl
    url(r'^home', views.home, name='home'),
    # 返却用ページのurl
    url(r'^retur', views.retur, name='retur'),
    # 蔵書リストのurl
    url(r'^book_list', views.book_list, name='book_list'),
    # 蔵書登録ページのurl
    url(r'^touroku', views.touroku, name='touroku'),
    # 予約確認ページのurl
    url(r'^reservation', views.reservation, name='reservation'),
    url('signup/', views.signup, name='signup'),
    url(r'dis_id/', views.regist_id, name='dis_id'),
    path('login/', auth_views.LoginView.as_view(template_name='regist/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

)
