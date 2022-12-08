from django.db import models


class TimeStampable(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Processable(models.Model):
    class Status(models.IntegerChoices):
        ACTIVE = 0
        PROCESSED = 1

    status = models.IntegerField(choices=Status.choices)

    class Meta:
        abstract = True
