# Generated by Django 2.2.1 on 2019-05-22 01:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Regist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book', models.CharField(max_length=100)),
                ('user', models.CharField(max_length=20)),
                ('day', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(max_length=10)),
                ('mail', models.CharField(max_length=30)),
            ],
        ),
    ]
