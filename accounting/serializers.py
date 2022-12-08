from rest_framework import serializers

from accounting.models import Courier, WeeklyIncome


class CourierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = ["id", "name"]


class WeeklyIncomeSerializer(serializers.ModelSerializer):
    courier = CourierSerializer(many=False, read_only=True)

    class Meta:
        model = WeeklyIncome
        fields = ["courier", "date", "amount"]
