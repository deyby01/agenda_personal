from time import timezone
from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.
class Tarea(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    completada = models.BooleanField(default=False)
    tiempo_estimado = models.DurationField(null=True, blank=True, help_text="Tiempo estimado para completar la tarea (ej. 2h30m)")
    fecha_asignada = models.DateField(null=True, blank=True, help_text="Día en que se planea realizar la tarea")

    proyecto = models.ForeignKey('Proyecto', on_delete=models.SET_NULL, null=True, 
                                blank=True, related_name='tareas', verbose_name='Proyecto',
                                help_text='Proyecto al que pertenece esta tarea (opcional)')
    
    def __str__(self):
        return self.titulo
    
    class Meta:
        ordering = ['usuario', 'fecha_asignada', 'titulo'] 
        

class Proyecto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE) # Un proyecto pertenece a un usuario
    nombre = models.CharField(max_length=255, verbose_name="Nombre del Proyecto")
    descripcion = models.TextField(null=True, blank=True, verbose_name="Descripción del Proyecto")
    tiempo_estimado_general = models.CharField(max_length=100, null=True, blank=True, verbose_name="Tiempo Estimado General", help_text="Ej: 1 semana, 2 meses, corto plazo")
    fecha_inicio = models.DateField(null=True, blank=True, verbose_name="Fecha de Inicio")
    fecha_fin_estimada = models.DateField(null=True, blank=True, verbose_name="Fecha de Finalización Estimada")

    # Podríamos añadir un estado, ej: 'planificado', 'en curso', 'completado', 'en espera'
    ESTADO_CHOICES = [
        ('planificado', 'Planificado'),
        ('en_curso', 'En Curso'),
        ('completado', 'Completado'),
        ('en_espera', 'En Espera'),
        ('cancelado', 'Cancelado'),
    ]
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='planificado',
        verbose_name="Estado del Proyecto"
    )
    fecha_creacion_proyecto = models.DateTimeField(auto_now_add=True)

    def get_completion_percentage(self):
        """
        Calcula el porcentaje de completacion del proyecto
        basado en las tareas asociadas
        """
        tareas_total = self.tareas.count()
        if tareas_total == 0:
            return 0.0

        tareas_completadas = self.tareas.filter(completada=True).count()
        porcentaje = (tareas_completadas / tareas_total) * 100
        return round(porcentaje, 1)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['usuario', 'fecha_fin_estimada', 'nombre']
        verbose_name = "Proyecto" # Nombre singular para el admin
        verbose_name_plural = "Proyectos" # Nombre plural para el admin


class Notification(models.Model):
    """
    Sistema de notificacion inteligentes
    Proposito: Alertas automaticas basadas en business logic
    Integracion: TaskPrioritizationEngine + ProjectProgressCalculator
    """
    # ===== Core fields =====
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario", help_text="Usuario que recibe la notificación")
    titulo = models.CharField(max_length=200, verbose_name='Titulo', help_text='Titulo breve y descriptivo de la notificación')
    mensaje = models.TextField(verbose_name='Mensaje', help_text='Contenido detallado de la notificación')

    # ===== CLASSIFICATION SYSTEM ======
    TIPO_CHOICES = [
        ('task', 'Tarea'),
        ('project', 'Proyecto'),
        ('system', 'Sistema'),
        ('achievement', 'Logro'),
    ]
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de Notificación"
    )

    SUBTIPO_CHOICES = [
        ('critical', 'Crítico'),
        ('warning', 'Advertencia'),
        ('info', 'Información'),
        ('success', 'Éxito'),
    ]
    subtipo = models.CharField(
        max_length=20,
        choices=SUBTIPO_CHOICES,
        verbose_name="Nivel de Urgencia"
    )

    # ===== STATE MANAGEMENT ======
    leida = models.BooleanField(default=False, verbose_name='Leída', help_text='Usuario ya vio la notificación')
    accionada = models.BooleanField(default=False, verbose_name='Accionada', help_text='Usuario ya actuo sobre la notificación')

    # ===== RELATIONS =====
    tarea_relacionada = models.ForeignKey(
        'Tarea',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Tarea Relacionada',
    )
    proyecto_relacionado = models.ForeignKey(
        'Proyecto',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Proyecto Relacionado',
    )

    # ======  METADATA ======
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_vencimiento = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Vencimiento', help_text='Cuando caduca la relevancia de esta notificación')

    # ===== BUSINESS LOGIC METADATA =====
    business_context = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Contexto de Business Logic',
        help_text = 'Datos adicionales del analisis que generó esta notificación'
    )

    def __str__(self):
        return f"{self.titulo} ({self.usuario.username})"

    @property
    def is_expired(self):
        """ Verifica si la notificación ya expiró """
        if not self.fecha_vencimiento:
            return False
        return timezone.now() > self.fecha_vencimiento

    @property
    def urgency_icon(self):
        """ Retorna el icono apropiado según el subtipo """
        icons = {
            'critical': '🚨',
            'warning': '⚠️',
            'info': 'ℹ️', 
            'success': '✅'
        }
        return icons.get(self.subtipo, '📢')

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        indexes = [
            models.Index(fields=['usuario', 'leida']),
            models.Index(fields=['usuario', 'tipo', 'subtipo']),
            models.Index(fields=['fecha_creacion']),
        ]
