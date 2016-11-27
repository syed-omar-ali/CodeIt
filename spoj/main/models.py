from django.db import models
from decimal import Decimal

class Profile(models.Model):
    username = models.CharField(max_length=30,default="")
    school = models.CharField(max_length=55,default="")
    img = models.CharField(max_length=100,default="")
    birthyear = models.CharField(max_length=30,default="")
    city = models.CharField(max_length=30,default="")
    solved = models.IntegerField(default=0)

    def __str__(self):
        return self.username


class Problem(models.Model):
    name = models.CharField(max_length=20,default="")
    user = models.CharField(max_length=30, default="alpha")
    memory = models.IntegerField(default=9999999999)
    time = models.DecimalField( max_digits=5, decimal_places=2, default=Decimal(10.000))

    def __str__(self):
        return self.name


class Synced(models.Model):
    user = models.CharField(max_length=30,default="")
    problem = models.CharField(max_length=20,default="")
    memory = models.CharField(max_length=100,default="")
    time = models.CharField(max_length=10,default="")
    date = models.CharField(default="",max_length=150)


    def __str__(self):
        return self.problem

class Follow(models.Model):
    user = models.CharField(max_length=30,default="")
    follows = models.CharField(max_length=30,default="")

    def __str__(self):
        return self.user


