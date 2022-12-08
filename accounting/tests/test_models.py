import datetime
import random

import pytest
from model_bakery import baker

from accounting.models import Courier, DailyIncome, Income
from miare.utils import get_yesterday_date


@pytest.mark.django_db
class TestDailyIncome:
    def test_courier_can_have_more_than_income_a_day(self):
        courier = baker.make(Courier)
        baker.make(Income, courier=courier, _quantity=2)

    def test_daily_is_sum_of_day_incomes(self):
        courier = baker.make(Courier)
        date = datetime.date.today()
        incomes = baker.make(
            Income, courier=courier, status=Income.Status.ACTIVE, _quantity=10
        )
        income_amount = sum(map(lambda i: i.get_signed_amount(), incomes))

        assert (
            DailyIncome.objects.get(courier=courier, date=date).amount == income_amount
        )

    def test_incomes_for_different_dates_and_couriers(self):
        def get_date():
            return datetime.date.today() - datetime.timedelta(random.randint(0, 300))

        dates = list(map(lambda _: get_date(), range(10)))
        couriers = baker.make(Courier, _quantity=10)

        def courier_income(courier, date):
            """return courier income summation in a specific date"""
            return sum(
                map(
                    lambda income: income.amount,
                    filter(
                        lambda income: income.courier.id == courier.id
                        and income.created_at.date() == date,
                        incomes,
                    ),
                )
            )

        incomes = []
        for _ in range(100):
            incomes.append(
                baker.make(
                    Income,
                    courier=random.choice(couriers),
                    created_at=random.choice(dates),
                )
            )

        for courier in couriers:
            for date in dates:
                di = DailyIncome.objects.filter(courier=courier, date=date)
                assert di.count() in [0, 1]
                if di.count() == 0:
                    assert courier_income(courier, date) == 0
                else:
                    di.first().amount == courier_income(courier, date)

    def test_negative_daily_income(self):
        courier = baker.make(Courier)
        date = datetime.date.today()
        incomes = baker.make(
            Income,
            courier=courier,
            status=Income.Status.ACTIVE,
            type=Income.Type.PUNISHMENT,
            _quantity=10,
        )
        income_sum = sum(map(lambda i: i.get_signed_amount(), incomes))
        assert DailyIncome.objects.get(courier=courier, date=date).amount == income_sum


@pytest.mark.django_db
class TestIncome:
    def test_get_yesterday_incomes_amount(self):
        yesterday = get_yesterday_date()
        incomes = []
        for _ in range(10):
            income = baker.make(Income, status=Income.Status.ACTIVE)
            income.created_at = yesterday
            income.save()
            incomes.append(income)
        assert Income.objects.get_yesterday_incomes_amount() == sum(
            map(lambda income: income.get_signed_amount(), incomes)
        )
