from django.urls import path  # path nos permite definir patrones de URL
from . import views          # Importamos el módulo views.py de nuestra app tareas
from .views import VistaRegistro  # Importamos la vista de registro de usuarios


urlpatterns = [
    path('', views.mi_semana_view, name='mi_semana_actual_url'),
    path('lista-tareas/', views.ListViewTasks.as_view(), name='lista_de_tareas_url'),
    path('nueva/', views.CreateViewTask.as_view(), name='crear_tarea_url'),
    path('tarea/<int:pk>/', views.DetailViewTask.as_view(), name='detalle_tarea_url'),
    path('editar/<int:pk>/', views.UpdateViewTask.as_view(), name='editar_tarea_url'),
    path('eliminar/<int:pk>/', views.DeleteViewTask.as_view(), name='eliminar_tarea_url'),
    
    
    path('registro/', VistaRegistro.as_view(), name='registro_url'),
    
    
    path('proyectos/', views.ListViewProjects.as_view(), name='lista_de_proyectos_url'),
    path('proyectos/<int:proyecto_id>/', views.detalle_proyecto, name='detalle_proyecto_url'),
    path('proyectos/nuevo/', views.crear_proyecto, name='crear_proyecto_url'),
    path('proyectos/editar/<int:proyecto_id>/', views.editar_proyecto, name='editar_proyecto_url'),
    path('proyectos/eliminar/<int:proyecto_id>/', views.eliminar_proyecto, name='eliminar_proyecto_url'),
    
    
    # URLs para la Vista Semanal
    
    # Para una semana específica basada en una fecha (año, mes, día)
    path('mi-semana/<int:anio>/<int:mes>/<int:dia>/', views.mi_semana_view, name='mi_semana_especifica_url'),
    
    path('tarea/cambiar-estado/<int:tarea_id>/', views.cambiar_estado_tarea, name='cambiar_estado_tarea_url'),
]