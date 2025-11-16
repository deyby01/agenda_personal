"""
Task Repository - Data access layer.

Migrated from tareas/repositories.TareaRepository
Single Responsibility: Task data access.
"""

from typing import Dict, List, Optional
from django.contrib.auth.models import User
from django.db.models import Q, QuerySet
import datetime

from apps.tasks.models import Tarea
from apps.core.utils import WeekRange


class TareaRepository:
    """
    Repository for Task data access.
    
    Single responsibility: ONLY queries and data access.
    """

    @staticmethod
    def get_tasks_for_user(user: User) -> QuerySet[Tarea]:
        """
        Gets all tasks for a user.

        Args:
            user (User): User who owns the tasks.

        Returns:
            QuerySet[Tarea]: User's tasks with project pre-fetched.
        """
        return Tarea.objects.filter(usuario=user).select_related('proyecto', 'usuario')


    @staticmethod
    def get_tasks_for_user_in_week(user: User, week_range: WeekRange) -> QuerySet[Tarea]:
        """
        Gets tasks for a user within a week range.

        Args:
            user (User): Task owner
            week_range (WeekRange): Date range for the week

        Returns:
            QuerySet[Tarea]: Tasks within the specified date range.
        """
        return Tarea.objects.filter(usuario=user, fecha_asignada__range=[week_range.start_date, week_range.end_date]).select_related('proyecto')


    
    @staticmethod
    def get_tasks_grouped_by_date(user: User, week_range: WeekRange) -> Dict[datetime.date, List[Tarea]]:
        """
        Groups tasks by assigned date for a week.

        Args:
            user (User): Task owner
            week_range (WeekRange): Date range

        Returns:
            Dict: {date: [Tasks]} for each day of the week
        """

        tareas = TareaRepository.get_tasks_for_user_in_week(user, week_range)

        # Initialize dict with all dates in the week
        grouped = {day: [] for day in week_range.days}

        # Group tasks by date
        for tarea in tareas:
            if tarea.fecha_asignada in grouped:
                grouped[tarea.fecha_asignada].append(tarea)

        return grouped


    @staticmethod
    def get_completed_tasks_count(user: User) -> int:
        """
        Counts completed tasks for a user.

        Args:
            user (User): Task owner

        Returns:
            int: Number of completed tasks
        """
        return Tarea.objects.filter(usuario=user, completada=True).count()


    @staticmethod
    def get_total_tasks_count(user: User) -> int:
        """
        Counts total tasks for a user.

        Args:
            user (User): Task owner

        Returns:
            int: Total number of tasks
        """
        return Tarea.objects.filter(usuario=user).count()


    
    @staticmethod
    def get_pending_tasks_for_user(user: User) -> QuerySet[Tarea]:
        """
        Gets pending tasks for a user.

        Args:
            user (User): Task owner

        Returns:
            QuerySet[Tarea]: Incomplete tasks
        """
        return Tarea.objects.filter(usuario=user, completada=False).select_related('proyecto')


    
    @staticmethod
    def get_overdue_tasks_for_user(user: User) -> QuerySet[Tarea]:
        """
        Gets overdue tasks (fecha_asignada < today and not completed)

        Args:
            user (User): Task owner

        Returns:
            QuerySet[Tarea]: Overdue tasks
        """
        from django.utils import timezone
        today = timezone.now().date()

        return Tarea.objects.filter(
            usuario=user,
            completada=False,
            fecha_asignada__lt=today
        ).select_related('proyecto')