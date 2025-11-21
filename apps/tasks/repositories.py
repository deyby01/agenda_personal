"""
Task Repository - Data access layer.

Migrado desde tareas/repositories.TareaRepository
Single Responsibility: Acceso a datos de tareas.
"""

from typing import Dict, List, Optional
from django.contrib.auth.models import User
from django.db.models import QuerySet, Q
import datetime

from apps.tasks.models import Tarea
from apps.core.utils import WeekRange


class TareaRepository:
    """
    Repository para acceso a datos de Tarea.
    
    Responsabilidad única: SOLO queries y acceso a datos.
    - No contiene lógica de negocio
    - No maneja presentación
    - No conoce sobre HTTP
    
    NOTA: Mantiene AMBAS APIs (antigua y nueva) para compatibilidad.
    """
    
    @staticmethod
    def get_tasks_for_user(user: User) -> QuerySet[Tarea]:
        """
        Obtiene todas las tareas de un usuario.
        
        Args:
            user: Usuario propietario
            
        Returns:
            QuerySet[Tarea]: Tareas del usuario con proyecto pre-cargado
        """
        return Tarea.objects.filter(
            usuario=user
        ).select_related('proyecto', 'usuario')
    
    @staticmethod
    def get_tasks_for_user_in_week(
        user: User,
        week_range: WeekRange
    ) -> QuerySet[Tarea]:
        """
        Obtiene tareas de un usuario en un rango de semana.
        
        Args:
            user: Usuario propietario
            week_range: Rango de fechas de la semana
            
        Returns:
            QuerySet[Tarea]: Tareas en el rango especificado
        """
        return Tarea.objects.filter(
            usuario=user,
            fecha_asignada__range=[week_range.start_date, week_range.end_date]
        ).select_related('proyecto')
    
    @staticmethod
    def get_tasks_grouped_by_date(
        user: User,
        week_range: WeekRange
    ) -> Dict[datetime.date, List[Tarea]]:
        """
        Agrupa tareas por fecha asignada para una semana.
        
        Args:
            user: Usuario propietario
            week_range: Rango de fechas
            
        Returns:
            Dict: {fecha: [tareas]} para cada día de la semana
        """
        tareas = TareaRepository.get_tasks_for_user_in_week(user, week_range)
        
        # Inicializar dict con todas las fechas de la semana
        grouped = {day: [] for day in week_range.days}
        
        # Agrupar tareas por fecha
        for tarea in tareas:
            if tarea.fecha_asignada in grouped:
                grouped[tarea.fecha_asignada].append(tarea)
        
        return grouped
    
    # ========== API ANTIGUA (week-based) - COMPATIBILIDAD ==========
    
    @staticmethod
    def get_completed_tasks_count(
        user: User,
        week_range: Optional[WeekRange] = None
    ) -> int:
        """
        Cuenta tareas completadas de un usuario.
        
        DUAL API:
        - Si se proporciona week_range: cuenta completadas EN LA SEMANA
        - Si NO se proporciona week_range: cuenta completadas TOTAL del usuario
        
        Args:
            user: Usuario propietario
            week_range: (Opcional) Rango de fechas de la semana
            
        Returns:
            int: Número de tareas completadas
        """
        if week_range:
            # API ANTIGUA: Contar completadas en la semana específica
            return TareaRepository.get_tasks_for_user_in_week(
                user, week_range
            ).filter(completada=True).count()
        else:
            # API NUEVA: Contar completadas totales del usuario
            return Tarea.objects.filter(
                usuario=user,
                completada=True
            ).count()
    
    @staticmethod
    def get_total_tasks_count(
        user: User,
        week_range: Optional[WeekRange] = None
    ) -> int:
        """
        Cuenta total de tareas de un usuario.
        
        DUAL API:
        - Si se proporciona week_range: cuenta tareas EN LA SEMANA
        - Si NO se proporciona week_range: cuenta tareas TOTALES del usuario
        
        Args:
            user: Usuario propietario
            week_range: (Opcional) Rango de fechas de la semana
            
        Returns:
            int: Número total de tareas
        """
        if week_range:
            # API ANTIGUA: Contar tareas en la semana específica
            return TareaRepository.get_tasks_for_user_in_week(
                user, week_range
            ).count()
        else:
            # API NUEVA: Contar tareas totales del usuario
            return Tarea.objects.filter(usuario=user).count()
    
    @staticmethod
    def get_tasks_without_date(user: User) -> QuerySet[Tarea]:
        """
        Obtiene tareas sin fecha asignada para un usuario.
        
        Args:
            user: Usuario propietario
        
        Returns:
            QuerySet[Tarea]: Tareas con fecha_asignada nula
        """
        return Tarea.objects.filter(
            usuario=user,
            fecha_asignada__isnull=True
        ).select_related('proyecto')
    
    # ========== API NUEVA (sin week_range) - CÓDIGO FUTURO ==========
    
    @staticmethod
    def get_pending_tasks_for_user(user: User) -> QuerySet[Tarea]:
        """
        Obtiene tareas pendientes de un usuario.
        
        Args:
            user: Usuario propietario
            
        Returns:
            QuerySet[Tarea]: Tareas no completadas
        """
        return Tarea.objects.filter(
            usuario=user,
            completada=False
        ).select_related('proyecto')
    
    @staticmethod
    def get_overdue_tasks_for_user(user: User) -> QuerySet[Tarea]:
        """
        Obtiene tareas atrasadas (fecha_asignada < hoy y no completadas).
        
        Args:
            user: Usuario propietario
            
        Returns:
            QuerySet[Tarea]: Tareas atrasadas
        """
        from django.utils import timezone
        today = timezone.localdate()
        
        return Tarea.objects.filter(
            usuario=user,
            completada=False,
            fecha_asignada__lt=today
        ).select_related('proyecto')
