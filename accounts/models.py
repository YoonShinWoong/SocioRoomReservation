from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    realname = models.TextField(max_length=20) # 성명ㅋ
    department = models.TextField(max_length=20) # 학과