from django.conf.urls import url
from . import views
app_name = "regist"
urlpatterns = (
    url(r'^regist', views.index, name='regist'),
    url(r'^home', views.home, name='home'),
    url(r'^retur', views.retur, name='retur'),
    url(r'^book_list', views.book_list, name='book_list'),
    url(r'^touroku', views.touroku,name='touroku')
)
