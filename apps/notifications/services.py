"""
Notification Services - Business Logic Layer.

Lógica de negocio para creación y gestión de notificaciones.
"""

from typing import Dict, Optional
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from apps.notifications.models import Notification
from apps.tasks.models import Tarea
from apps.projects.models import Proyecto


class NotificationService:
    """
    Servicio para creación y gestión de notificaciones.
    
    Single Responsibility: Lógica de negocio de notificaciones.
    """
    
    @staticmethod
    def create_task_notification(
        user: User,
        tarea: Tarea,
        titulo: str,
        mensaje: str,
        subtipo: str = 'info'
    ) -> Notification:
        """
        Crea notificación relacionada a una tarea.
        
        Args:
            user: Usuario que recibe la notificación
            tarea: Tarea relacionada
            titulo: Título de la notificación
            mensaje: Mensaje de la notificación
            subtipo: Subtipo de urgencia
            
        Returns:
            Notification: Notificación creada
        """
        return Notification.objects.create(
            usuario=user,
            titulo=titulo,
            mensaje=mensaje,
            tipo='task',
            subtipo=subtipo,
            tarea_relacionada=tarea
        )
    
    @staticmethod
    def create_project_notification(
        user: User,
        proyecto: Proyecto,
        titulo: str,
        mensaje: str,
        subtipo: str = 'info'
    ) -> Notification:
        """
        Crea notificación relacionada a un proyecto.
        
        Args:
            user: Usuario que recibe la notificación
            proyecto: Proyecto relacionado
            titulo: Título de la notificación
            mensaje: Mensaje de la notificación
            subtipo: Subtipo de urgencia
            
        Returns:
            Notification: Notificación creada
        """
        return Notification.objects.create(
            usuario=user,
            titulo=titulo,
            mensaje=mensaje,
            tipo='project',
            subtipo=subtipo,
            proyecto_relacionado=proyecto
        )
    
    @staticmethod
    def create_overdue_task_notification(tarea: Tarea) -> Notification:
        """
        Crea notificación para tarea atrasada.
        
        Args:
            tarea: Tarea atrasada
            
        Returns:
            Notification: Notificación creada
        """
        return Notification.objects.create(
            usuario=tarea.usuario,
            titulo=f"Tarea Atrasada: {tarea.titulo}",
            mensaje=f"La tarea '{tarea.titulo}' estaba programada para {tarea.fecha_asignada} y aún no está completada.",
            tipo='task',
            subtipo='warning',
            tarea_relacionada=tarea,
            business_context={
                'dias_atrasada': (timezone.localdate() - tarea.fecha_asignada).days,
                'fecha_asignada': str(tarea.fecha_asignada)
            }
        )
    
    @staticmethod
    def create_achievement_notification(
        user: User,
        titulo: str,
        mensaje: str,
        context: Optional[Dict] = None
    ) -> Notification:
        """
        Crea notificación de logro.
        
        Args:
            user: Usuario que recibe el logro
            titulo: Título del logro
            mensaje: Mensaje descriptivo
            context: Contexto adicional (opcional)
            
        Returns:
            Notification: Notificación de logro creada
        """
        return Notification.objects.create(
            usuario=user,
            titulo=titulo,
            mensaje=mensaje,
            tipo='achievement',
            subtipo='success',
            business_context=context,
            fecha_vencimiento=timezone.now() + timedelta(days=7)
        )
