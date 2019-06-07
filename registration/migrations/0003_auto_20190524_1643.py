# Generated by Django 2.2.1 on 2019-05-24 07:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0002_auto_20190523_1342'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wtr', models.CharField(max_length=30)),
            ],
        ),
        migrations.AlterField(
            model_name='registration',
            name='day',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]