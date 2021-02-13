# Generated by Django 3.1.6 on 2021-02-13 00:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название', max_length=200)),
                ('model', models.CharField(help_text='Модель', max_length=200)),
                ('system_id', models.IntegerField(help_text='ID Груза')),
                ('date', models.DateField(help_text='Дата')),
                ('time_in', models.TimeField(help_text='Время погрузки')),
                ('time_out', models.TimeField(help_text='Время отгрузки')),
                ('vendor', models.CharField(help_text='Изготовитель', max_length=200)),
                ('rfid', models.IntegerField(default=0, help_text='ID RFID метки', unique=True)),
                ('address', models.IntegerField(help_text='Назначенная ячейка', unique=True)),
                ('state', models.CharField(choices=[('created', 'Задача поставленна'), ('spawn', 'В пути на конвеер'), ('moving_in', 'На конвеере: Едет до погрузчика'), ('elevator', 'На погрузке'), ('storage', 'Хранение'), ('moving_out', 'На конвеере: Едет на отгрузку'), ('destroyed', 'Отгружено')], default='created', help_text='Состояние', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now=True)),
                ('text', models.CharField(max_length=1000)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
