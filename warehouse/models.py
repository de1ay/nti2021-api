from django.contrib.auth.models import User
from django.db import models


class Item(models.Model):
    # Metadata
    name = models.CharField(max_length=200, name='Название')
    model = models.CharField(max_length=200, name='Модель')
    system_id = models.IntegerField(name='ID Груза')
    date = models.DateField(name='Дата')
    time_in = models.TimeField(name='Время погрузки')
    time_out = models.TimeField(name='Время отгрузки')
    vendor = models.CharField(max_length=200, name='Изготовитель')
    # Storage
    STATES = [
        ('created', 'Задача поставленна'),
        ('spawn', 'В пути на конвеер'),
        ('moving_in', 'На конвеере: Едет до погрузчика'),
        ('elevator', 'На погрузке'),
        ('storage', 'Хранение'),
        ('moving_out', 'На конвеере: Едет на отгрузку'),
        ('destroyed', 'Отгружено'),
    ]
    rfid = models.IntegerField(name='ID RFID метки', default=0, unique=True)
    address = models.IntegerField(name='Назначенная ячейка', unique=True)
    state = models.CharField(max_length=10, choices=STATES, default='created', name='Состояние')

    def __str__(self):
        return self.name


class Log(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False)
    datetime = models.DateTimeField(auto_now=True)
    text = models.CharField(max_length=1000)

    def __str__(self):
        return self.text
