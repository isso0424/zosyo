from django.conf.urls import url
from . import views
app_name = "regist"
urlpatterns = [
    url(r'^regist', views.index, name='regist'),
    url(r'^home/',views.home,name='home')
]