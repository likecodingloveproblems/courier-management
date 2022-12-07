from django.contrib import admin

from accounting.models import DailyIncome, Income, WeeklyIncome


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    pass


@admin.register(DailyIncome)
class DailyIncomeAdmin(admin.ModelAdmin):
    pass


@admin.register(WeeklyIncome)
class WeeklyIncomeAdmin(admin.ModelAdmin):
    pass
