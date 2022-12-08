from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext as _

from accounting.managers import DailyIncomeManager, IncomeManager, WeeklyIncomeManager
from accounting.mixins import Processable, TimeStampable


class Courier(models.Model):

    name = models.CharField(_("name"), max_length=50)

    class Meta:
        verbose_name = _("Courier")
        verbose_name_plural = _("Couriers")

    def __str__(self):
        return self.name


class Income(TimeStampable, Processable, models.Model):
    """Income store every courier income events, include:
    - trip income
    - reward income
    - punishment income
    the amount of income is positive but punish is negative and is recognized by it's type
    A locking process is necessary, so after a period of time or immediately,
    records must be lock for update to guarantee data consistency."""

    class Type(models.IntegerChoices):
        TRIP = 0
        REWARD = 1
        PUNISHMENT = 2

    objects = IncomeManager()
    courier = models.ForeignKey(
        "accounting.Courier", verbose_name=_("courier"), on_delete=models.PROTECT
    )
    type = models.IntegerField(choices=Type.choices)
    amount = models.PositiveIntegerField(_("amount"))

    class Meta:
        verbose_name = _("Trip")
        verbose_name_plural = _("Trips")

    def __str__(self):
        return f"{self.courier}: {self.amount}"

    def get_signed_amount(self):
        if self.type == self.Type.PUNISHMENT:
            return self.amount * -1
        return self.amount

    def update_income_status(self):
        self.status = self.Status.PROCESSED
        self.save(update_fields=["status"])

    def is_processed(self):
        return self.status == self.Status.PROCESSED


class CumulativeIncome(models.Model):
    """Cumulative of income models

    This is an abstract model to be used as superclass of daily and weekly incomes
    """

    courier = models.ForeignKey(
        "accounting.Courier", verbose_name=_("courier"), on_delete=models.PROTECT
    )
    date = models.DateField(_("date"), auto_now=False, auto_now_add=True)
    amount = models.IntegerField(_("amount"))

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.courier}: {self.amount}-{self.date}"


class DailyIncome(Processable, CumulativeIncome):

    objects = DailyIncomeManager()

    class Meta:
        verbose_name = _("DailyIncome")
        verbose_name_plural = _("DailyIncomes")
        constraints = [
            UniqueConstraint(
                fields=["date", "courier"],
                name="courier_date_unique_together_daily_income",
            )
        ]

    def _update_daily_amount(self, income: Income):
        self.amount += income.get_signed_amount()


class WeeklyIncome(CumulativeIncome):

    objects = WeeklyIncomeManager()

    class Meta:
        verbose_name = _("weeklyincome")
        verbose_name_plural = _("weeklyincomes")
        constraints = [
            UniqueConstraint(
                fields=["date", "courier"],
                name="courier_date_unique_together_weekly_income",
            )
        ]
