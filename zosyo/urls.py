"""zosyo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.utils.functional import curry
from django.views.defaults import *
from django.http import HttpResponse
urlpatterns = [
    path('admin/', admin.site.urls),
    path('registration/', include('registration.urls', namespace="regist")),
    path('accounts/', include('allauth.urls')),
    path('', lambda request: HttpResponse('インデックス'), name='index'),
]
handler404 = curry(server_error, template_name='base.html')
