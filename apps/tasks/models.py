"""
Task Domain Model.

Migrated from tareas.models.Tarea with improvements:
- Inherits from UserOwnedModel (DRY)
- Better documentation
- FK to Proyecto from apps.projects
"""

from django.db import models
from apps.core.models import UserOwnedModel
from apps.projects.models import Proyecto

class Tarea(UserOwnedModel):
    """
    Represents an individual task that can be associated with a project.
    
    Business Rules:
    - A task belongs to a user (UserOwnedModel)
    - A task can be associated with a project (optional)
    - If the project is deleted, the task is not deleted (SET_NULL)
    - Tasks have a status: completed (True/False)
    """

    titulo = models.CharField(max_length=200, verbose_name="Title", help_text='Descriptive title of the task')
    descripcion = models.TextField(blank=True, null=True, verbose_name="Description", help_text='Detailed description of the task')
    completada = models.BooleanField(default=False, verbose_name='Completed', help_text='Indicates if the task is completed')
    tiempo_estimado = models.DurationField(null=True, blank=True, verbose_name='Estimated time', help_text='Estimated time to complete the task (e.g., 2h30m)')
    fecha_asignada = models.DateField(null=True, blank=True, verbose_name='Assigned Date', help_text='Day when the task is planned to be completed')
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tareas',
        verbose_name='Project',
        help_text='Project to which this task belongs (Optional)'
    )

    @property
    def is_completed(self):
        """
        Alias for completada (completed)

        Returns:
            bool: True if the task is completed
        """
        return self.completada

    @property
    def is_overdue(self):
        """
        Indicates if the task is overdue

        Returns:
            bool: True if fecha_asignada < today and not completed
        """
        if not self.fecha_asignada or self.completada:
            return False
        
        from django.utils import timezone
        today = timezone.now().date()
        return self.fecha_asignada < today

    @property
    def project_name(self):
        """
        Gets the project name (if exists).

        Returns:
            str: Project name or "No project"
        """
        return self.proyecto.nombre if self.proyecto else "No project"

    def __str__(self):
        status = "✅" if self.completada else "⬜"
        return f"{status} {self.titulo}"

    class Meta:
        ordering = ['usuario', 'fecha_asignada', 'titulo']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        indexes = [
            models.Index(fields=['usuario', 'completada']),
            models.Index(fields=['usuario', 'fecha_asignada']),
            models.Index(fields=['proyecto', 'completada']),
        ]