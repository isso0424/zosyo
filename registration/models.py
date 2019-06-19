from django.db import models
from django.contrib import admin
from django.contrib.auth.models import AbstractUser, UserManager


# データベースのモデルを作成するクラス達
# 蔵書の基本データベース
class Registration(models.Model):
    # 本の名前を入れる
    # chaffedは文字列用の型
    book = models.CharField(max_length=100)
    # ユーザー名を入れる
    user = models.CharField(max_length=20)
    # 日付を入れる
    # defaultは最初に何を入れておくか
    day = models.CharField(max_length=20, default='なし')
    # 本が貸出中かどうかを入れる
    status = models.CharField(max_length=10)
    # メアドを入れる
    mail = models.CharField(max_length=30)
    # 予約してる人を入れる
    who_want = models.CharField(max_length=20)


# 予約用データベース
class Reservation(models.Model):
    # 予約する本を一時的に入れる
    # nullは空を認めるということ
    wtr = models.CharField(max_length=30, null=True)
    # 予約する人を一時的に入れる
    who = models.CharField(max_length=20, null=True)


# 検索用データベース
class Search(models.Model):
    # 検索結果用データベース
    search_book = models.CharField(max_length=20, null=True)
    TF = models.CharField(max_length=5, null=True)


class RegistAdmin(admin.ModelAdmin):
    list_display = ('book', )

    def registration(self, instance):
        return instance


class User(AbstractUser):
    objects = UserManager()

    class Meta(object):
        app_label = 'accounts'
