import datetime

from django.db.models import QuerySet


class ProcessableQuerySet:
    """Processable QuerySet to defined logic for models that are processable"""

    def processed(self):
        """filter queryset with status=PROCESSED"""
        return self.filter(status=self.model.Status.PROCESSED)


class DateTimeQuerySet:
    """Processable QuerySet to defined logic for models that are processable
    date_field is specified to make queries on date_field"""

    date_field = "date"

    def yesterday(self):
        """filter queryset with date_field=yesterday"""
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        return self.filter(**{self.date_field: yesterday})


class IncomeQuerySet(ProcessableQuerySet, DateTimeQuerySet, QuerySet):
    date_field = "created_at__date"


class DailyIncomeQuerySet(DateTimeQuerySet, QuerySet):
    pass
