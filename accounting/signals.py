from django.db.models.signals import post_save
from django.dispatch import receiver

from accounting.models import DailyIncome, Income


@receiver(post_save, sender=Income)
def update_daily_income(sender, instance, **kwargs):
    """On every new income of courier, his/her daily income is updated"""
    DailyIncome.objects.update_income(instance)


def connecting():
    """only for the sake of linters"""
    print("accounting signals connected!")
