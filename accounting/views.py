from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import mixins, permissions, viewsets
from rest_framework.filters import OrderingFilter

from accounting.filters import WeeklyIncomeFilters
from accounting.models import WeeklyIncome
from accounting.serializers import WeeklyIncomeSerializer


class WeeklyIncomeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = WeeklyIncome.objects.all()
    serializer_class = WeeklyIncomeSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["date"]
    filterset_class = WeeklyIncomeFilters

    def get_queryset(self):
        return super().get_queryset().select_related("courier")

    @extend_schema(
        description="Get courier weekly incomes",
        examples=[
            OpenApiExample(
                "get couriers weekly income for 2022-12-03",
                value=[
                    {
                        "courier": {
                            "id": 3,
                            "name": "courier 1",
                        },
                        "date": "2022-12-03",
                        "amount": 1929690195,
                    },
                    {
                        "courier": {
                            "id": 4,
                            "name": "courier 2",
                        },
                        "date": "2022-12-03",
                        "amount": 492635180,
                    },
                    {
                        "courier": {
                            "id": 7,
                            "name": "courier 3",
                        },
                        "date": "2022-12-03",
                        "amount": 889983411,
                    },
                ],
            )
        ],
        parameters=[
            OpenApiParameter(
                "from_date",
                type=OpenApiTypes.DATE,
                description="""filter results after this date""",
                examples=[
                    OpenApiExample(
                        "Get weekly incomes after 2022-12-01", value="2022-12-01"
                    ),
                ],
            ),
            OpenApiParameter(
                "to_date",
                type=OpenApiTypes.DATE,
                description="""filter results before this date""",
                examples=[
                    OpenApiExample(
                        "Get weekly incomes before 2022-12-01", value="2022-12-01"
                    ),
                ],
            ),
            OpenApiParameter(
                "ordering",
                type=OpenApiTypes.DATE,
                description="order results based on the date",
                examples=[
                    OpenApiExample("ascending ordering by date", "date"),
                    OpenApiExample("descending ordering by date", "-date"),
                ],
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
