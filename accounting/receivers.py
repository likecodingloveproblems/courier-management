import logging

from accounting.exceptions import IncomeIsGeneratedAsProcessed
from accounting.models import DailyIncome

logger = logging.getLogger(__name__)


def update_daily_income(sender, instance, created, **kwargs):
    """Update daily income

    Update daily income of courier on that date
    for simplicity purposes updating of income is ignored!
    only created and active incomes are take into the effect
    if instance is created as processed or processed before this receiver
    IncomeIsGeneratedAsProcessed will be caught and logged(mailed to admin users)
    to be review by admin users.


    Args:
        sender (django.db.models.signals.post_save): post_save signal of database
        instance (accounting.models.Income): income instance
        created (bool): instance is created?
    """
    if created:
        try:
            DailyIncome.objects.update_income(instance)
        except IncomeIsGeneratedAsProcessed:
            """log this income to be reviewed later"""
            income_dict = {
                "id": instance.id,
                "courier id": instance.courier_id,
                "type": instance.get_type_display(),
                "status": instance.get_status_display(),
                "created at": instance.created_at,
            }
            logger.critical(
                f"Income is generated with processed status! Income:{income_dict}"
            )
