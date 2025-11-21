from django.urls import path
from apps.notifications import views

urlpatterns = [
    path('centro-notificaciones/', views.NotificationCenterView.as_view(), name='centro_notificaciones'),
    path('notificacion/<int:notification_id>/click/', views.NotificationClickView.as_view(), name='notification_click'),
]