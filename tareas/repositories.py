"""
Repository Layer - Data access abstraction following SOLID principles

Este modulo implementa el patron Repository para separar el acceso a datos
de la logica de negocio, cumpliendo con Dependency Inversion Principle(DIP)
"""
from typing import Dict, List, Optional, Any
from django.contrib.auth.models import User
from django.db.models import QuerySet
import datetime

from .models import Tarea, Proyecto
from .services import WeekRange

class TareaRepository:
    """
    Repository para acceso a datos de tarea.

    single responsability: SOLO maneja queries y acceso a datos de tarea.
    - No contiene logica de negocio.
    - NO maneja presentacion
    - No conoce sobre HTTP requests/responses

    Esto permite:
    - Testing independiente con datos mock
    - Cambios en query sin afectar business logic
    - Diferentes estrategias de persistencia (DB, cache, etc)
    """

    @staticmethod
    def get_tasks_for_user(user: User) -> QuerySet[Tarea]:
        """
        Obtiene todas las tareas de un usuario

        Args:
            user: Usuario Django
        Returns:
            QuerySet de Tarea filtrado por usuario
        """
        return Tarea.objects.filter(usuario=user).select_related('proyecto')

    @staticmethod
    def get_tasks_for_user_in_week(user: User, week_range: WeekRange) -> QuerySet[Tarea]:
        """
        Obtiene tareas de un usuario en una semana especifica

        Args:
            user: Usuario Django
            week_range: Rango de fechas de la semana
        Returns:
            QuerySet de Tarea filtrado por usuario y rango de fechas
        """
        return Tarea.objects.filter(
            usuario=user,
            fecha_asignada__range=[week_range.start_date, week_range.end_date]
        ).select_related('proyecto').order_by('fecha_asignada', 'tiempo_estimado')

    @staticmethod 
    def get_tasks_grouped_by_date(user: User, week_range: WeekRange) -> Dict[datetime.date, List[Tarea]]:
        f"""
        Obtiene tareas agrupadas por fecha para una semana.

        Args:
            user: Usuario Django
            week_range: Rango de fechas de la semana
        Returns:
            Diccionario fecha: [Lista_de_tareas]
        """        
        tasks = TareaRepository.get_tasks_for_user_in_week(user, week_range)

        # Inicializar Diccionario
        tasks_by_date = {day: [] for day in week_range.days}

        # Agrupar tareas por fecha
        for task in tasks:
            if task.fecha_asignada in tasks_by_date:
                tasks_by_date[task.fecha_asignada].append(task)
            
        return tasks_by_date
    
    @staticmethod
    def get_completed_tasks_count(user: User, week_range: WeekRange) -> int:
        """
        Cuenta tareas completadas en una semana.

        Args: 
            user: Usuario Django
            week_range: Rango de fechas de la semana
        Returns:
            Númera de tareas completadas
        """
        return TareaRepository.get_tasks_for_user_in_week(user, week_range).filter(
            completada=True
        ).count()

    @staticmethod
    def get_total_tasks_count(user: User, week_range: WeekRange) -> int:
        """
        Cuenta tareas totales en una semana.

        Args: 
            user: Usuario Django
            week_range: Rango de fechas de la semana
        Returns:
            Número total de tareas
        """
        return TareaRepository.get_tasks_for_user_in_week(user, week_range).count()


class ProyectoRepository:
    """
    Repository para acceso a datos de Proyecto.
    
    Single Responsibility: SOLO maneja queries de Proyecto.
    """
    
    @staticmethod
    def get_active_projects_for_user(user: User) -> QuerySet[Proyecto]:
        """
        Obtiene proyectos activos de un usuario.    
        
        Args:
            user: Usuario Django
            
        Returns:
            QuerySet de Proyecto activos del usuario
        """
        return Proyecto.objects.filter(
            usuario=user,
            estado='en_curso'
        ).order_by('nombre')
    
    @staticmethod
    def get_project_with_tasks_stats(user: User, project_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un proyecto con estadísticas de tareas.
        
        Args:
            user: Usuario Django
            project_id: ID del proyecto
            
        Returns:
            Diccionario con proyecto y estadísticas o None
        """
        try:
            project = Proyecto.objects.get(id=project_id, usuario=user)
            
            total_tasks = project.tareas.count()
            completed_tasks = project.tareas.filter(completada=True).count()
            
            completion_percentage = 0
            if total_tasks > 0:
                completion_percentage = round((completed_tasks / total_tasks) * 100, 1)
            
            return {
                'project': project,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'completion_percentage': completion_percentage
            }
        except Proyecto.DoesNotExist:
            return None

    @staticmethod
    def get_active_projects_for_user_in_period(user: User, start_date: datetime.date, end_date: datetime.date) -> QuerySet[Proyecto]:
        """
        Obtiene proyectos activos de un usuario en un período específico.
        Replica la lógica compleja del código original.
        
        Args:
            user: Usuario Django
            start_date: Fecha inicio del período
            end_date: Fecha fin del período
            
        Returns:
            QuerySet de Proyecto activos en el período
        """
        from django.db.models import Q
        
        return Proyecto.objects.filter(
            Q(usuario=user),
            (
                Q(fecha_inicio__lte=end_date, fecha_fin_estimada__gte=start_date) |
                Q(fecha_inicio__lte=end_date, fecha_fin_estimada__isnull=True) |
                Q(fecha_inicio__isnull=True, fecha_fin_estimada__gte=start_date) |
                Q(fecha_inicio__isnull=True, fecha_fin_estimada__isnull=True)
            ),
            ~Q(estado__in=['completado', 'cancelado'])
        ).distinct().order_by('fecha_fin_estimada', 'nombre')
