"""
Modelos base abstractos que heredan todas las entidades del dominio.

Siguiendo el principio DRY (Don't Repeat Yourself):
- TimeStampedModel: Timestamps automáticos
- UserOwnedModel: Relación con usuario + timestamps
"""

from django.db import models
from django.contrib.auth.models import User

class TimeStampedModel(models.Model):
    """
    Abstract base class con timestamps automaticos.

    Todos los modelos del proyecto que necesitan auditoria
    de creación/modificación heredan de este.

    Benefits:
    - DRY: No repetir fecha_creacion en cada modelo
    - Consistency: Mismo comportamiento en todos los modelos
    - Maintainability: Un solo lugar para cambiar comportamiento
    """
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación',
        help_text='Timestamp automático de creación',
    )

    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Modificación',
        help_text='Timestamp automático de ultima modificación',
    )

    class Meta:
        abstract = True
        ordering = ['-fecha_creacion']


class UserOwnedModel(TimeStampedModel):
    """
    Abstract base para modelos que pertenecen a un usuario.

    Hereda de TimestampModel (trae timestamps) y añade:
    - Relación con User
    - Metodos helper para ownership

    Usado por: Tarea, Proyecto, Notificacion
    """

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario',
        help_text='Usuario propietario de este recurso',
        related_name='%(app_label)s_%(class)s_related',
    )

    class Meta:
        abstract = True
        ordering = ['-fecha_creacion']

    def is_owned_by(self, user: User) -> bool:
        """
        Helper method: Verifica si el recurso pertence al usuario.

        Args:
            user: Usuario a verificar
        Returns:
            bool: True si el usuario es el propietario
        """
        return self.usuario == user