# Generated by Django 2.2.1 on 2019-06-07 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0005_auto_20190529_0945'),
    ]

    operations = [
        migrations.CreateModel(
            name='Search',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_book', models.CharField(max_length=20, null=True)),
            ],
        ),
    ]
