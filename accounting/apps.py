from django.apps import AppConfig
from django.db.models.signals import post_save


class AccountingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounting"

    def ready(self) -> None:
        from accounting import receivers

        post_save.connect(receivers.update_daily_income, "accounting.Income")
