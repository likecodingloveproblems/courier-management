from django.db import models, transaction
from django.db.models import Case, DateField, F, Sum, Value, When

from accounting.exceptions import IncomeIsGeneratedAsProcessed
from accounting.querysets import DailyIncomeQuerySet, IncomeQuerySet
from miare.utils import get_this_and_past_saturday


class IncomeManager(models.Manager):
    def get_queryset(self):
        return IncomeQuerySet(self.model, using=self._db)

    def get_yesterday_incomes_amount(self):
        """Get yesterday incomes

        get yesterday incomes summation of amount and return 0 if there is nothing

        Returns:
            int: summation of amount
        """
        result = (
            self.get_queryset()
            .yesterday()
            .processed()
            .annotate(
                signed_amount=Case(
                    When(type=self.model.Type.PUNISHMENT, then=F("amount") * -1),
                    default=F("amount"),
                )
            )
            .aggregate(Sum("signed_amount"))
            .get("signed_amount__sum", 0)
        )
        return result if result else 0


class DailyIncomeManager(models.Manager):
    def get_queryset(self):
        return DailyIncomeQuerySet(self.model, using=self._db)

    def get_yesterday_daily_incomes_amount(self):
        """Return yesterday daily incomes summation amount

        Returns:
            int: 0 or positive integer
        """
        result = self.get_queryset().yesterday().aggregate(Sum("amount"))["amount__sum"]
        return result if result else 0

    def get_weekly_report(self):
        """return weekly report to be used in creating weekly income objects
        return objects is a"""
        this_saturday, past_saturday = get_this_and_past_saturday()
        return (
            self.get_queryset()
            .filter(
                date__gte=past_saturday,
                date__lt=this_saturday,
                status=self.model.Status.ACTIVE,
            )
            .values("courier_id")
            .annotate(
                amount=Sum("amount"),
                date=Value(past_saturday, output_field=DateField()),
            )
            .values_list("courier_id", "date", "amount")
        )

    def update_last_week_daily_income_status(self):
        """Process last week daily income objects

        When weekly income is created, their related daily income status must be set to PROCESSED
        """
        this_saturday, past_saturday = get_this_and_past_saturday()
        self.get_queryset().filter(
            date__gte=past_saturday, date__lt=this_saturday
        ).update(status=self.model.Status.PROCESSED)

    def get_daily_income(self, income):
        """Get daily income

        get daily income of for an income courier in the same date or
        create one instance without saving it to database with status=ACTIVE and amount=0

        Args:
            income (accounting.models.Income): an instance of Income model

        Returns:
            accounting.models.DailyIncome: a not saved instance of DailyIncome model
        """
        daily_income, _ = (
            self.get_queryset()
            .select_for_update()
            .get_or_create(
                courier_id=income.courier.id,
                date=income.created_at.date(),
                defaults={"amount": 0, "status": self.model.Status.ACTIVE},
            )
        )
        return daily_income

    def update_income(self, income) -> None:
        """Update courier daily income, based on the new income

        We must Guaranty that two concurrent request don't override
        so handle race condition we use select_for_update to lock database row
        and we use atomic transaction to ensure that the
        income and daily income either both updated or none of them effected

        Args:
            income (accounting.models.Income): a saved instance of Income instance send here by post_save signal

        Raises:
            IncomeIsGeneratedAsProcessed: if income instance is processed, can't be processed another time
        """
        if income.is_processed():
            raise IncomeIsGeneratedAsProcessed()
        daily_income = self.get_daily_income(income)
        daily_income._update_daily_amount(income)
        with transaction.atomic():
            daily_income.save()
            income.update_income_status()

    def create(self, **kwargs):
        raise NotImplementedError

    def update(self, **kwargs):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError


class WeeklyIncomeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def create_weekly_income(self, report):
        """Create all weekly incomes

        weekly income is generated based on a task in every saturday
        and all related daily income records are updated as processed

        Args:
            report (List[List[courier_id(Int), date(Date), amount(Int)]]):
                report parameter is generated and seed to this function
                and used for bulk_create of all weekly incomes
        """
        weekly_incomes = []
        for courier_id, date, amount in report:
            weekly_incomes.append(
                self.model(courier_id=courier_id, date=date, amount=amount)
            )
        self.bulk_create(weekly_incomes)
