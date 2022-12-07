from django.db import models, transaction

from accounting.models import Income


class DailyIncomeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def update_income(self, income: Income) -> None:
        """update courier daily income, based on the new income

        We must Guaranty that two concurrent request don't override
        so handle race condition we use select_for_update to lock database row
        and we use atomic transaction to ensure that the
        income and daily income either both updated or none of them effected"""
        try:
            daily_income = (
                self.get_queryset()
                .select_for_update()
                .get(courier__id=income.courier.id, date=income.created_at.date())
            )
            daily_income.amount = daily_income + income.get_signed_amount()
        except self.model.DoesNotExists:
            daily_income = self.model(courier=income.courier, amount=income.amount)
        with transaction.atomic():
            daily_income.save()
            income.processed()
