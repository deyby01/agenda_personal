"""
Notification Views - View layer para Notifications domain.

Migrado desde tareas/views.py con mejoras:
- Imports actualizados a nueva arquitectura
- Uso de Repositories
- Mejor separación de responsabilidades
- Docstrings comprehensivos
"""

from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.notifications.models import Notification
from apps.notifications.repositories import NotificationRepository

class NotificationCenterView(LoginRequiredMixin, ListView):
    """
    Centro de notificaciones del usuario.
    
    Features:
    - Todas las notificaciones del usuario
    - Diferenciación visual (leídas vs no leídas)
    - Ordenadas por fecha (más recientes primero)
    - Paginación para performance
    - Estadísticas en contexto
    
    Template: notificaciones/centro_notificaciones.html
    Context: notificaciones (QuerySet de Notification)
    """
    model = Notification
    template_name = 'notificaciones/centro_notificaciones.html'
    context_object_name = 'notificaciones'
    paginate_by = 20

    def get_queryset(self):
        """
        Obtiene notificaciones del usuario con relaciones precargadas.
        
        Returns:
            QuerySet[Notification]: Notificaciones del usuario ordenadas
        """
        return NotificationRepository.get_all_for_user(self.request.user).order_by('-fecha_creacion')

    def get_context_data(self, **kwargs):
        """
        Añade estadísticas de notificaciones al contexto.
        
        Returns:
            dict: Context con estadísticas completas
        """
        context = super().get_context_data(**kwargs)
        user_notifications = self.get_queryset()

        context.update({
            'total_notifications': user_notifications.count(),
            'unread_count': NotificationRepository.get_unread_count(self.request.user),
            'read_count': user_notifications.filter(leida=True).count(),
            'critical_count': user_notifications.filter(subtipo='critical').count(),
            'warning_count': user_notifications.filter(subtipo='warning').count(),
        })
        return context


class NotificationClickView(LoginRequiredMixin, View):
    """
    Manejo de click en notificación.
    
    Features:
    - Marcar notificación como leída
    - Redirigir al origen (tarea/proyecto relacionado)
    - Actualizar contador automáticamente
    - Mensajes de feedback
    
    URL: /agenda/notificaciones/<notification_id>/click/
    """

    def get(self, request, notification_id):
        """
        Procesa click en notificación.
        
        Args:
            request: HttpRequest
            notification_id: ID de la notificación
            
        Returns:
            HttpResponse: Redirect a origen (tarea/proyecto) o centro
        """
        try:
            notification = Notification.objects.get(
                id=notification_id,
                usuario=request.user
            )
        except Notification.DoesNotExist:
            messages.error(request, 'Notificación no encontrada.')
            return redirect('centro_notificaciones')

        # Marcar como leida
        notification.mark_as_read()

        # Redirect inteligente segun relacion
        if notification.tarea_relacionada:
            messages.success(request, f'Revisando tarea: {notification.tarea_relacionada.titulo}')
            return redirect('detalle_tarea_url', pk=notification.tarea_relacionada.id)
        elif notification.proyecto_relacionado:
            messages.success(request, f'Revisando proyecto: {notification.proyecto_relacionado.nombre}')
            return redirect('detalle_proyecto_url', pk=notification.proyecto_relacionado.id)
        else:
            # Notificación sin relación especifica
            messages.info(request, 'Notificación marcada como leida.')

            