"""
Project Domain Model.

Migrado desde tareas.models.Proyecto con mejoras:
- Hereda de UserOwnedModel (DRY)
- Mejor documentación
- Properties para computed values
- Indices para performance
"""

from django.db import models
from apps.core.models import UserOwnedModel

class Proyecto(UserOwnedModel):
    """
    Representa un proyecto que agrupa múltiples tareas.
    
    Un proyecto tiene:
    - Estado (planificado, en curso, completado, etc.)
    - Fechas de inicio y fin
    - Tiempo estimado
    - Relación con múltiples tareas
    
    Business Rules:
    - Un usuario puede tener múltiples proyectos
    - Un proyecto puede tener múltiples tareas
    - Las tareas son opcionales (proyecto sin tareas es válido)
    """

    ESTADO_CHOICES = [
        ('planificado', 'Planificado'),
        ('en_curso', 'En Curso'),
        ('completado', 'Completado'),
        ('en_espera', 'En Espera'),
        ('cancelado', 'Cancelado'),
    ]

    nombre = models.CharField(
        max_length=255,
        verbose_name='Nombre del Proyecto',
        help_text='Nombre descriptivo del proyecto',
    )

    descripcion = models.TextField(
        null=True,
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción detallada del proyecto',
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='planificado',
        verbose_name='Estado',
        help_text='Estado actual del proyecto',
    )

    fecha_inicio = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Inicio'
    )

    fecha_fin_estimada = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Fin Estimada'
    )

    tiempo_estimado_general = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Tiempo Estimado General',
        help_text='Tiempo total estimado (ej: 40 horas)'
    )

    def get_completion_percentage(self):
        """
        Calcula el porcentaje de completación del proyecto.

        Returns:
            float: Porcentaje de tareas completadas (0-100)
        
        Example:
            >>> proyecto.get_completion_percentage()
            75.5 # 75.5% de tareas completadas
        """

        tareas_total = self.tareas.count()
        if tareas_total == 0:
            return 0.0
            
        tareas_completadas = self.tareas.filter(completada=True).count()
        return round((tareas_completadas / tareas_total) * 100, 1)

    
    @property
    def is_active(self):
        """
        Verifica si el proyecto esta activo.

        Returns:
            bool: True si el proyecto esta en curso o planificado
        """
        return self.estado in ['planificado', 'en_curso', 'en_espera']

    @property
    def total_tareas(self):
        """
        Numero total de tareas en el proyecto.
        """
        return self.tareas.count()

    @property
    def tareas_completadas(self):
        """
        Numero de tareas completadas.
        """
        return self.tareas.filter(completada=True).count()

    @property
    def tareas_pendientes(self):
        """
        Numero de tareas pendientes.
        """
        return self.tareas.filter(completada=False).count()

    def __str__(self):
        return f"{self.nombre} ({self.get_estado_display()})"

    
    class Meta:
        ordering = ['usuario', 'fecha_fin_estimada', 'nombre']
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        indexes = [
            models.Index(fields=['usuario', 'estado']),
            models.Index(fields=['fecha_fin_estimada']),
        ]