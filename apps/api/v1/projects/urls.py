from rest_framework.routers import DefaultRouter

from apps.api.v1.projects.views import ProyectoViewSet

router = DefaultRouter()
router.register("projects", ProyectoViewSet, basename="projects")

urlpatterns = router.urls


