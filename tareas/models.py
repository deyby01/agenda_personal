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

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['usuario', 'fecha_fin_estimada', 'nombre']
        verbose_name = "Proyecto" # Nombre singular para el admin
        verbose_name_plural = "Proyectos" # Nombre plural para el admin