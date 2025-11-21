from django.urls import path
from apps.projects import views

urlpatterns = [
    # Mantiene rutas históricas bajo /agenda/proyectos/ para evitar conflictos
    path('proyectos/', views.ListViewProjects.as_view(), name='lista_de_proyectos_url'),
    path('proyectos/<int:pk>/', views.DetailViewProject.as_view(), name='detalle_proyecto_url'),
    path('proyectos/nuevo/', views.CreateViewProject.as_view(), name='crear_proyecto_url'),
    path('proyectos/editar/<int:pk>/', views.UpdateViewProject.as_view(), name='editar_proyecto_url'),
    path('proyectos/eliminar/<int:pk>/', views.DeleteViewProject.as_view(), name='eliminar_proyecto_url'),
]