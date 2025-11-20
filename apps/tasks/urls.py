"""
Task URLs - URL routing para Tasks domain.

Migrado desde tareas/urls.py
IMPORTANTE: Mantiene nombres originales para compatibilidad con templates.
"""

from django.urls import path
from apps.tasks import views

# NO usar app_name por ahora (causa conflictos con nombres existentes)

urlpatterns = [
    # Mi Semana (Main view)
    path('', views.MyWeekView.as_view(), name='mi_semana_actual_url'),
    path('mi-semana/<int:year>/<int:week>/', views.MyWeekView.as_view(), name='mi_semana_url'),
    
    # Task CRUD - Mantiene nombres originales
    path('lista-tareas/', views.ListViewTasks.as_view(), name='lista_de_tareas_url'),
    path('nueva/', views.CreateViewTask.as_view(), name='crear_tarea_url'),
    path('tarea/<int:pk>/', views.DetailViewTask.as_view(), name='detalle_tarea_url'),
    path('editar/<int:pk>/', views.UpdateViewTask.as_view(), name='editar_tarea_url'),
    path('eliminar/<int:pk>/', views.DeleteViewTask.as_view(), name='eliminar_tarea_url'),
    
    # Quick actions
    path('tarea/cambiar-estado/<int:pk>/', views.ToggleTaskStatusView.as_view(), name='cambiar_estado_tarea_url'),
]
