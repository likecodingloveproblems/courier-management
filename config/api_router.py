from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from accounting.views import WeeklyIncomeViewSet
from miare.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("weekly-incomes", WeeklyIncomeViewSet, basename="weekly-incomes")


app_name = "api"
urlpatterns = router.urls
