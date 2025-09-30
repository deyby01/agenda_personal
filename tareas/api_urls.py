from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r"tareas", views.TareaViewSet, basename='tarea')
router.register(r"proyectos", views.ProyectoViewSet, basename='proyecto')

urlpatterns = [
    path('', include(router.urls)),
]