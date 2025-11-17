"""
Notification Domain Model.

Smart notification system for task and project events.
"""

from django.db import models
from django.db.models.expressions import OrderByList
from django.utils import timezone
from apps.core.models import UserOwnedModel
from apps.tasks.models import Tarea
from apps.projects.models import Proyecto


class Notification(UserOwnedModel):
    """
    Intelligent system notification.
    
    Business Rules:
    - A notification belongs to a user
    - It can be related to a Task (optional)
    - It can be related to a Project (optional)
    - It has a type (task/project/system/achievement)
    - It has a subtype (critical/warning/info/success)
    - It can expire automatically
    """

    TIPO_CHOICES = [
        ('task', 'Tarea'),
        ('project', 'Proyecto'),
        ('system', 'Sistema'),
        ('achievement', 'Logro')
    ]

    SUBTIPO_CHOICES = [
        ('critical', 'Crítico'),
        ('warning', 'Advertencia'),
        ('info', 'Información'),
        ('success', 'Éxito'),
    ]

    titulo = models.CharField(max_length=200, verbose_name='Titulo', help_text='Titulo breve de la notificacion')
    mensaje = models.TextField(verbose_name='Mensaje', help_text='Contenido detallado de la notificacion')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo', help_text='Categoria de la notificacion')
    subtipo = models.CharField(max_length=20, choices=SUBTIPO_CHOICES, verbose_name='Subtipo', help_text='Nivel de urgencia o importancia')
    leida = models.BooleanField(default=False, verbose_name='Leida', help_text='Indica si el usuario ha leido la notificacion')
    accionada = models.BooleanField(default=False, verbose_name='Accionada', help_text='Indica si el usuario ha tomado acción sobre la notificacion')

    tarea_relacionada = models.ForeignKey(
        Tarea,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificaciones',
        verbose_name='Tarea Relacionada',
        help_text='Tarea asociada a esta notificación',
    )

    proyecto_relacionado = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificaciones',
        verbose_name='Proyecto Relacionado',
        help_text='Proyecto asociado a esta notificación',
    )

    fecha_vencimiento = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Vencimiento',
        help_text='Fecha en que la notificación expira'
    )
    
    business_context = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Contexto de Negocio',
        help_text='Datos adicionales en formato JSON'
    )

    
    @property
    def is_expired(self):
        """
        Checks if the notification has expired.

        Returns:
            bool: True if fecha_vencimiento < now
        """
        if not self.fecha_vencimiento:
            return False
        return timezone.now() > self.fecha_vencimiento

    @property
    def urgency_icon(self):
        """
        Gets the urgency icon according to the subtype.
        
        Returns:
            str: Emoji representing the subtype
        """
        icons = {
            'critical': '🚨',
            'warning': '⚠️',
            'info': 'ℹ️',
            'success': '✅'
        }
        return icons.get(self.subtipo, '📢')


    @property
    def is_unread(self):
        """
        Checks if the notification has not been read.

        Returns:
            bool: True if it is not read.
        """
        return not self.leida

    @property
    def requires_action(self):
        """
        Checks if the notification requires action.

        Returns:
            bool: True if it is critical or warning and not actioned.
        """
        return self.subtipo in ['critical', 'warning'] and not self.accionada

    def mark_as_read(self):
        """ Marks the notification as read """
        self.leida = True
        self.save(update_fields=['leida'])

    def mark_as_actioned(self):
        """ Marks the notification as actioned """
        self.accionada = True
        self.leida = True
        self.save(update_fields=['accionada', 'leida'])

    def __str__(self):
        return f"{self.urgency_icon} {self.titulo} ({self.usuario.username})"

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        indexes = [
            models.Index(fields=['usuario', 'leida']),
            models.Index(fields=['usuario', 'tipo', 'subtipo']),
            models.Index(fields=['fecha_creacion']),
            models.Index(fields=['tarea_relacionada']),
            models.Index(fields=['proyecto_relacionado']),
        ]