"""
Project Repository - Data access layer.

Migrado desde tareas/repositories.ProyectoRepository
Responsabilidad única: acceso a datos de proyectos.
"""

from typing import Dict, List, Optional
from django.contrib.auth.models import User
from django.db.models import QuerySet, Count, Q
import datetime

from apps.projects.models import Proyecto


class ProyectoRepository:
    """
    Repository para acceso a datos de Proyecto.

    Single Responsability: Solo queries y acceso a datos.
    - No contiene logica de negocio
    - No maneja presentacion
    - No conoce sobre HTTP requests/responses
    """

    @staticmethod
    def get_active_projects_for_user(user: User) -> QuerySet[Proyecto]:
        """
        Obtiene proyectos activos de un usuario.

        Args:
            user (User): Usuario propietario

        Returns:
            QuerySet[Proyecto]: Proyectos activos ordenados
        """

        return Proyecto.objects.filter(
            usuario=user
        ).exclude(
            estado__in=['completado', 'cancelado']
        ).order_by('fecha_fin_estimada', 'nombre')

    
    @staticmethod
    def get_project_with_tasks_stats(project_id: int, user: User) -> Optional[Dict]:
        """
        Obtiene un proyecto con estadísticas de tareas.

        Args:
            project_id (int): ID del proyecto
            user (User): Usuario propietario

        Returns:
            Optional[Dict]: Dict con proyecto y stat, o None si no existe
        """
        try:
            proyecto = Proyecto.objects.get(
                id=project_id,
                usuario=user
            )

            return {
                'proyecto': proyecto,
                'total_tareas': proyecto.total_tareas,
                'tareas_completadas': proyecto.tareas_completadas,
                'tareas_pendientes': proyecto.tareas_pendientes,
                'completion_percentage': proyecto.get_completion_percentage(),
            }
        
        except Proyecto.DoesNotExist:
            return None
        
        
    
    @staticmethod
    def get_active_projects_for_user_in_period(user: User, start_date: datetime.date, end_date: datetime.date) -> QuerySet[Proyecto]:
        """
        Obtiene proyectos activos en un periodo especifico.

        Args:
            user (User): Usuario propietario
            start_date (datetime.date): Fecha de inicio del periodo
            end_date (datetime.date): Fecha de fin del periodo

        Returns:
            QuerySet[Proyecto]: Proyectos en el periodo
        """

        return Proyecto.objects.filter(
            usuario=user,
            estado__in=['planificado', 'en_curso', 'en_espera'],
        ).filter(
            Q(fecha_inicio__lte=end_date) | Q(fecha_inicio__isnull=True),
            Q(fecha_fin_estimada__gte=start_date) | Q(fecha_fin_estimada__isnull=True)
        ).distinct()


    @staticmethod
    def get_all_projects_for_user(user: User) -> QuerySet[Proyecto]:
        """
        Obtiene todos los proyectos de un usuario.

        Args:
            user (User): Usuario propietario

        Returns:
            QuerySet[Proyecto]: Todos los proyectos del usuario
        """
        return Proyecto.objects.filter(
            usuario=user
        )

    
    @staticmethod
    def get_completed_projects_count(user:User) -> int:
        """
        Obtiene el numero de proyectos completados de un usuario.

        Args:
            user (User): Usuario propietario

        Returns:
            int: Numero de proyectos completados
        """
        return Proyecto.objects.filter(
            usuario=user,
            estado='completado'
        ).count()