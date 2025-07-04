from django.urls import path 
from . import views          
from .views import VistaRegistro  


urlpatterns = [
    path('', views.MyWeekView.as_view(), name='mi_semana_actual_url'),
    path('lista-tareas/', views.ListViewTasks.as_view(), name='lista_de_tareas_url'),
    path('nueva/', views.CreateViewTask.as_view(), name='crear_tarea_url'),
    path('tarea/<int:pk>/', views.DetailViewTask.as_view(), name='detalle_tarea_url'),
    path('editar/<int:pk>/', views.UpdateViewTask.as_view(), name='editar_tarea_url'),
    path('eliminar/<int:pk>/', views.DeleteViewTask.as_view(), name='eliminar_tarea_url'),
        
    path('registro/', VistaRegistro.as_view(), name='registro_url'),  
    
    path('proyectos/', views.ListViewProjects.as_view(), name='lista_de_proyectos_url'),
    path('proyectos/<int:pk>/', views.DetailViewProject.as_view(), name='detalle_proyecto_url'),
    path('proyectos/nuevo/', views.CreateViewProject.as_view(), name='crear_proyecto_url'),
    path('proyectos/editar/<int:pk>/', views.UpdateViewProject.as_view(), name='editar_proyecto_url'),
    path('proyectos/eliminar/<int:pk>/', views.DeleteViewProject.as_view(), name='eliminar_proyecto_url'),
    
    # URLs para la Vista Semanal
    # Para una semana específica basada en una fecha (año, mes, día)
    path('mi-semana/<int:anio>/<int:mes>/<int:dia>/', views.MyWeekView.as_view(), name='mi_semana_especifica_url'),
    path('tarea/cambiar-estado/<int:tarea_id>/', views.ToggleTaskStatusView.as_view(), name='cambiar_estado_tarea_url'),
]