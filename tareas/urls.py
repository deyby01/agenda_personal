from django.urls import path  # path nos permite definir patrones de URL
from . import views          # Importamos el módulo views.py de nuestra app tareas
from .views import VistaRegistro  # Importamos la vista de registro de usuarios

# urlpatterns es una lista de patrones de URL que Django buscará.
# Es un nombre especial que Django espera encontrar.
urlpatterns = [
    # Cuando un usuario visite la URL raíz de esta aplicación de tareas (ej. /agenda/),
    # se llamará a la función 'lista_tareas' que está en views.py.
    # El argumento 'name="lista_tareas"' le da un nombre a esta URL,
    # lo cual es útil para referenciarla desde otras partes de Django (como plantillas).
    path('', views.lista_tareas, name='lista_de_tareas_url'),
    path('nueva/', views.crear_tarea, name='crear_tarea_url'),
    # Ej: /agenda/editar/1/ llamará a views.editar_tarea(request, tarea_id=1)
    path('editar/<int:tarea_id>/', views.editar_tarea, name='editar_tarea_url'),
    path('eliminar/<int:tarea_id>/', views.eliminar_tarea, name='eliminar_tarea_url'),
    # La ruta será '/agenda/registro/' si el prefijo en el urls.py principal es 'agenda/'
    path('registro/', VistaRegistro.as_view(), name='registro_url'),
    
    path('proyectos/', views.lista_proyectos, name='lista_de_proyectos_url'),
    
    # NUEVA URL para crear proyectos
    path('proyectos/nuevo/', views.crear_proyecto, name='crear_proyecto_url'),
    
    # NUEVA URL para editar proyectos
    path('proyectos/editar/<int:proyecto_id>/', views.editar_proyecto, name='editar_proyecto_url'),
    
    # NUEVA URL para eliminar proyectos
    path('proyectos/eliminar/<int:proyecto_id>/', views.eliminar_proyecto, name='eliminar_proyecto_url'),
    
    # URLs para la Vista Semanal
    # Para la semana actual (sin parámetros de fecha en la URL)
    path('mi-semana/', views.mi_semana_view, name='mi_semana_actual_url'),
    # Para una semana específica basada en una fecha (año, mes, día)
    path('mi-semana/<int:anio>/<int:mes>/<int:dia>/', views.mi_semana_view, name='mi_semana_especifica_url'),
    
    path('tarea/cambiar-estado/<int:tarea_id>/', views.cambiar_estado_tarea, name='cambiar_estado_tarea_url'),
]