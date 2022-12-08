import datetime
import random

import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from accounting.models import WeeklyIncome


@pytest.fixture
def url():
    return reverse("api:weekly-incomes-list")


@pytest.fixture
def weekly_incomes():
    weekly_incomes = baker.make(WeeklyIncome, _quantity=5)
    # update datetime
    for income in weekly_incomes:
        income.date -= datetime.timedelta(random.randint(0, 20))
        income.save()
    return weekly_incomes


@pytest.mark.django_db
class TestWeeklyIncomeViewSet:
    def weekly_incomes_to_expected_results(self, weekly_incomes):
        return [
            {
                "courier": {"id": income.courier.id, "name": income.courier.name},
                "date": str(income.date),
                "amount": income.amount,
            }
            for income in weekly_incomes
        ]

    def test_only_staff_users_allowed(self, client, url):
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_weekly_incomes(self, admin_client, url, weekly_incomes):
        response = admin_client.get(url)
        expected_json = self.weekly_incomes_to_expected_results(weekly_incomes)
        assert response.json() == expected_json

    def test_date_ascending_ordering(self, admin_client, url, weekly_incomes):
        ascending_ordering = "?ordering=date"
        response = admin_client.get(url + ascending_ordering)
        weekly_incomes.sort(key=lambda income: income.date)
        expected_json = self.weekly_incomes_to_expected_results(weekly_incomes)
        assert response.json() == expected_json

    def test_date_descending_ordering(self, admin_client, url, weekly_incomes):
        descending_ordering = "?ordering=-date"
        response = admin_client.get(url + descending_ordering)
        weekly_incomes.sort(key=lambda income: (income.date, income.id), reverse=True)
        expected_json = self.weekly_incomes_to_expected_results(weekly_incomes)
        assert response.json() == expected_json

    def test_filter_datetime(self, admin_client, url):
        dates = [
            datetime.date(2022, 1, 1),
            datetime.date(2022, 1, 4),
            datetime.date(2022, 1, 5),
            datetime.date(2022, 1, 6),
            datetime.date(2022, 1, 7),
            datetime.date(2022, 1, 10),
            datetime.date(2022, 1, 11),
            datetime.date(2022, 1, 12),
        ]
        incomes = []
        for date in dates:
            income = baker.make(WeeklyIncome)
            income.date = date
            income.save()
            incomes.append(income)
        from_date = datetime.date(2022, 1, 5)
        to_date = datetime.date(2022, 1, 10)
        expected_count = 4
        url += f"?from_date={from_date}&to_date={to_date}"
        response = admin_client.get(url)
        assert len(response.json()) == expected_count
