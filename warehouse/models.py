from django.contrib.auth.models import User
from django.db import models


class Item(models.Model):
    # Metadata
    name = models.CharField(max_length=200, help_text='Название')
    model = models.CharField(max_length=200, help_text='Модель')
    system_id = models.IntegerField(help_text='ID Груза')
    date = models.DateField(help_text='Дата')
    time_in = models.TimeField(help_text='Время погрузки')
    time_out = models.TimeField(help_text='Время отгрузки')
    vendor = models.CharField(max_length=200, help_text='Изготовитель')
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
    rfid = models.IntegerField(help_text='ID RFID метки', default=0)
    address = models.IntegerField(help_text='Назначенная ячейка', unique=True)
    state = models.CharField(max_length=10, choices=STATES, default='created', help_text='Состояние')

    def __str__(self):
        return self.name + ' |Инв№ ' + str(self.system_id)


class Log(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False)
    datetime = models.DateTimeField(auto_now=True)
    text = models.CharField(max_length=1000)

    def __str__(self):
        return self.text
