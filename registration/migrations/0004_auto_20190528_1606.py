# Generated by Django 2.2.1 on 2019-05-28 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0003_auto_20190524_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='day',
            field=models.CharField(default=None, max_length=20),
        ),
    ]
