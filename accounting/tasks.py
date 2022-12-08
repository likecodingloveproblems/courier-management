import logging

from celery import shared_task
from django.db import transaction

from accounting.models import DailyIncome, Income, WeeklyIncome
from miare.utils import get_five_minutes_ago, get_yesterday_date

logger = logging.getLogger(__name__)


@shared_task
def calculate_weekly_incomes():
    """Create weekly incomes

    This Task ran on every saturday morning and create all weekly incomes of courier
    based on their last week daily incomes
    """
    weekly_income_report = DailyIncome.objects.get_weekly_report()
    with transaction.atomic():
        WeeklyIncome.objects.create_weekly_income(weekly_income_report)
        DailyIncome.objects.update_last_week_daily_income_status()


@shared_task
def process_failed_income_update():
    """Process daily incomes with active status

    This task will fetch daily incomes before five minutes ago that are not processed by signal
    or their process failed, It's a retry to update daily income and make income as processed
    """
    five_minutes_ago = get_five_minutes_ago()
    incomes = Income.objects.filter(
        created_at__lte=five_minutes_ago, status=Income.Status.ACTIVE
    )
    for income in incomes:
        DailyIncome.objects.update_income(income)


@shared_task
def check_daily_balance():
    """Check daily balance with income records

    This task check yesterday daily income and income balance to be equal
    in midnight, if they were not equal, something went wrong and must be reviewed
    and a log sent to admin email.
    """
    yesterday_income = Income.objects.get_yesterday_incomes_amount()
    yesterday_daily_income = DailyIncome.objects.get_yesterday_daily_incomes_amount()
    if yesterday_daily_income != yesterday_income:
        logger.critical(
            f"""Unbalanced income in {get_yesterday_date()}
            daily_income{yesterday_daily_income}, income:{yesterday_income}"""
        )
