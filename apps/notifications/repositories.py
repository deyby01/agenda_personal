"""
Notification Repository - Data access layer.

Single Responsibility: Acceso a datos de notificaciones.
"""

from typing import List, Optional
from django.contrib.auth.models import User
from django.db.models import QuerySet, Q
from django.utils import timezone

from apps.notifications.models import Notification


class NotificationRepository:
    """
    Repository para acceso a datos de Notification.
    
    Responsabilidad única: SOLO queries y acceso a datos.
    """

    @staticmethod
    def get_all_for_user(user:User) -> QuerySet[notificacion]:
        """
        Obtiene todas las notificaciones de un usuario.

        Args:
            user (User): Usuario propietario

        Returns:
            QuerySet[notificacion]: Notificaciones ordenadas por fecha
        """
        return Notification.objects.filter(
            usuario=user
        ).select_related(
            'tarea_relacionada',
            'proyecto_relacionado',
            'usuario'
        )

    
    @staticmethod
    def get_unread_for_user(user: User) -> QuerySet[Notification]:
        """
        Obtiene notificaciones no leidas de un usuario.

        Args:
            user (User): Usuario propietario

        Returns:
            QuerySet[Notification]: Notificaciones no leidas 
        """
        return Notification.objects.filter(
            usuario=user,
            leida=False
        ).select_related(
            'tarea_relacionada',
            'proyecto_relacionado'
        )


    @staticmethod
    def get_unread_count(user: User) -> int:
        """
        Cuenta notificaciones no leidas

        Args:
            user (User): Usuario propietario

        Returns:
            int: Cantidad de notificaciones no leidas
        """
        return Notification.objects.filter(
            usuario=user,
            leida=False
        ).count()

    
    @staticmethod
    def get_critical_unread(user: User) -> QuerySet[Notification]:
        """
        Obtiene notificaciones criticas no leidas.

        Args:
            user (User): Usuario propietario

        Returns:
            QuerySet[Notification]: Notificaciones criticas sin leer.
        """
        return Notification.objects.filter(
            usuario=user,
            leida=False,
            subtipo='critical'
        ).select_related(
            'tarea_relacionada',
            'proyecto_relacionado'
        )

    
    @staticmethod
    def get_by_type(user: User, tipo: str) -> QuerySet[Notification]:
        """
        Obtiene notificaciones por tipo.

        Args:
            user (User): Usuario propietario
            tipo (str): Tipo de notificacion (task/project/system/achievement)

        Returns:
            QuerySet[Notification]: Notificaciones del tipo especificado.
        """
        return Notification.objects.filter(
            usuario=user,
            tipo=tipo
        ).select_related(
            'tarea_relacionada',
            'proyecto_relacionado'
        )

    
    @staticmethod
    def get_recent(user: User, days: int = 7) -> QuerySet[Notification]:
        """
        Obtiene notificaciones recientes.

        Args:
            user (User): Usuario propietario
            days (int, optional): Numero de dias hacia atras (default: 7).

        Returns:
            QuerySet[Notification]: Notificaciones de últimos 7 dias
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        return Notification.objects.filter(
            usuario=user,
            fecha_creacion__gte=cutoff_date
        ).select_related(
            'tarea_relacionada',
            'proyecto_relacionado'
        )


    @staticmethod
    def mark_all_as_read(user: User) -> int:
        """
        Marca todas las notificaciones como leidas.

        Args:
            user (User): Usuario propietario

        Returns:
            int: Número de notificaciones actualizadas.
        """
        return Notification.objects.filter(
            usuario=user,
            leida=False
        ).update(leida=True)

    
    @staticmethod
    def delete_old_notifications(user: User, days: int = 30) -> int:
        """
        Elimina notificaciones antiguas leidas.

        Args:
            user (User): Usuario propietario
            days (int, optional): Dias de antiguedad (default: 30).

        Returns:
            int: Número de notificaciones eliminadas.
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        deleted, _ = Notification.objects.filter(
            usuario=user,
            leida=True,
            fecha_creacion__lt=cutoff_date
        ).delete()
        return deleted