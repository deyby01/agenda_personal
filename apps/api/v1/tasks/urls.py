from rest_framework.routers import DefaultRouter

from apps.api.v1.tasks.views import TareaViewSet

router = DefaultRouter()
router.register("tasks", TareaViewSet, basename="tasks")

urlpatterns = router.urls


