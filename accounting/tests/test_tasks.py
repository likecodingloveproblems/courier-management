import datetime

import pytest
from django.db.models import Sum
from django.db.models.signals import post_save
from model_bakery import baker

from accounting.models import DailyIncome, Income, WeeklyIncome
from accounting.receivers import update_daily_income
from accounting.tasks import (
    calculate_weekly_incomes,
    check_daily_balance,
    process_failed_income_update,
)
from miare.utils import get_five_minutes_ago, get_yesterday_date


@pytest.mark.django_db
class TestWeeklyIncome:
    def test_processed_daily_income_does_not_involve_another_time(self):
        daily_incomes = baker.make(
            DailyIncome, status=DailyIncome.Status.PROCESSED, _quantity=5
        )
        for income in daily_incomes:
            income.date = income.date - datetime.timedelta(1)
            income.save()
        assert WeeklyIncome.objects.count() == 0
        calculate_weekly_incomes()
        assert WeeklyIncome.objects.count() == 0

    def test_active_daily_incomes_are_calculated_in_last_week(self):
        date = datetime.date.today() - datetime.timedelta(1)
        daily_incomes = baker.make(
            DailyIncome, status=DailyIncome.Status.ACTIVE, date=date, _quantity=5
        )
        for income in daily_incomes:
            income.date = income.date - datetime.timedelta(1)
            income.save()
        assert WeeklyIncome.objects.count() == 0
        calculate_weekly_incomes()
        assert WeeklyIncome.objects.aggregate(Sum("amount"))["amount__sum"] == sum(
            map(lambda i: i.amount, daily_incomes)
        )

    def test_only_past_seven_days_daily_income_are_calculated(self):
        daily_incomes = baker.make(
            DailyIncome, status=DailyIncome.Status.ACTIVE, amount=100, _quantity=4
        )
        timedeltas = [
            datetime.timedelta(-3),
            datetime.timedelta(0),
            datetime.timedelta(1),
            datetime.timedelta(7),
            datetime.timedelta(8),
            datetime.timedelta(14),
        ]
        for income, timedelta in zip(daily_incomes, timedeltas):
            income.date -= timedelta
            income.save()

        weekly_income = daily_incomes[2].amount + daily_incomes[3].amount
        calculate_weekly_incomes()
        assert (
            WeeklyIncome.objects.aggregate(Sum("amount"))["amount__sum"]
            == weekly_income
        )
        assert (
            DailyIncome.objects.filter(status=DailyIncome.Status.PROCESSED).count() == 2
        )


@pytest.fixture
def disconnect_update_daily_income_receiver():
    post_save.disconnect(update_daily_income, sender=Income)
    yield None
    post_save.connect(update_daily_income, sender=Income)


@pytest.mark.django_db
class TestActiveDailyIncome:
    def test_processed_daily_income_are_ignored(
        self, disconnect_update_daily_income_receiver
    ):
        incomes = baker.make(Income, status=Income.Status.ACTIVE, _quantity=5)
        for income in incomes:
            income.created_at = get_five_minutes_ago()
            income.save()
        assert DailyIncome.objects.count() == 0
        process_failed_income_update()
        assert DailyIncome.objects.count() > 0
        assert not Income.objects.filter(status=Income.Status.ACTIVE).exists()


@pytest.mark.django_db
class TestSystemBalance:
    def test_balance_daily_income_with_income(self):
        count = 300
        incomes = []
        for _ in range(count):
            incomes.append(baker.make(Income, status=Income.Status.ACTIVE))
        total_incomes = sum(map(lambda income: income.get_signed_amount(), incomes))
        print(Income.objects.filter(status=Income.Status.ACTIVE).values())
        assert not Income.objects.filter(status=Income.Status.ACTIVE).exists()
        assert (
            DailyIncome.objects.aggregate(Sum("amount"))["amount__sum"] == total_incomes
        )

    def test_unbalance_daily_income_on_disconnecting_update_daily_income_receiver(
        self, disconnect_update_daily_income_receiver
    ):
        count = 300
        incomes = []
        for i in range(count):
            incomes.append(baker.make(Income, status=Income.Status.ACTIVE))
            if i > count / 2:
                post_save.connect(update_daily_income, sender=Income)
        total_incomes = sum(map(lambda income: income.get_signed_amount(), incomes))
        assert Income.objects.filter(status=Income.Status.ACTIVE).exists()
        assert (
            DailyIncome.objects.aggregate(Sum("amount"))["amount__sum"] != total_incomes
        )

    def test_check_daily_balance_task(self):
        yesterday = get_yesterday_date()
        incomes = baker.make(Income, _quantity=30)
        for income in incomes[:20]:
            income.date = yesterday
            income.save()
        check_daily_balance()
