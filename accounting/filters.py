from django_filters import rest_framework as filters

from accounting.models import WeeklyIncome


class WeeklyIncomeFilters(filters.FilterSet):
    from_date = filters.DateFilter(field_name="date", lookup_expr="gte")
    to_date = filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = WeeklyIncome
        fields = ["from_date", "to_date"]
