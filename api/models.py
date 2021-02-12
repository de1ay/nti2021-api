from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False)
    fio = models.CharField(max_length=100)
    about = models.CharField(max_length=2000)
    number = models.CharField(max_length=30)
    avatar = models.ImageField(blank=True)

    def __str__(self):
        return self.user.username


class UserOtp(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False)
    otp = models.CharField(max_length=10)

    def __str__(self):
        return self.user.username
