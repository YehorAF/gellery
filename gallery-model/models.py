from django.core.validators import MinLengthValidator
from django.db import models


STATUSES = [
    ("admin", "admin"),
    ("user", "user")
]


class User(models.Model):
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=20, unique=True, validators=[MinLengthValidator(8)])
    fullname = models.CharField(max_length=250)
    password = models.CharField(max_length=250)
    salt = models.CharField(max_length=16)
    session = models.CharField(max_length=64)
    status = models.CharField(max_length=20, choices=STATUSES)


class Picture(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.CharField(max_length=1024)
    description = models.TextField()
    tags = models.TextField()


class Follower(models.Model):
    influencer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="influencer")
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower")


class Reaction(models.Model):
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)