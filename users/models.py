from django.db import models
from django.db.models.base import Model

class User(models.Model):
    name = models.CharField(max_length=20)
    nickname = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    class Meta:
        db_table="users"