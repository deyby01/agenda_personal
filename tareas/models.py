from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.
class Tarea(models.Model):
    # NUEVO CAMPO PARA EL USUARIO:
    # ForeignKey establece una relación de muchos a uno (un usuario puede tener muchas tareas).
    # User: El modelo de usuario incorporado de Django.
    # on_delete=models.CASCADE: Si un usuario es eliminado, todas sus tareas también se eliminarán.
    # null=True, blank=True: Hacemos esto temporalmente para las tareas existentes que no tienen usuario.
    # Una vez que todos los usuarios estén asociados, podríamos considerar quitar null=True si cada tarea DEBE tener un usuario.
    # O mejor aún, lo hacemos no nulo y manejamos las migraciones para datos existentes.
    # Para un proyecto nuevo, es mejor hacerlo no nulo desde el principio si siempre va a haber un usuario.
    # Por ahora, para facilitar la migración con datos existentes (si los hubiera, aunque creo que no tienes datos críticos aún):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    completada = models.BooleanField(default=False)

    # Campo para el tiempo estimado que tomará la tarea.
    # models.DurationField almacena un periodo de tiempo.
    # null=True y blank=True lo hacen opcional, por si alguna tarea no tiene un estimado.
    tiempo_estimado = models.DurationField(null=True, blank=True, help_text="Tiempo estimado para completar la tarea (ej. 2h30m)")

    # Campo para la fecha en que se debe realizar o vencer la tarea.
    # Esto será útil para la vista de calendario/semanal.
    # Lo hacemos opcional por si hay tareas sin fecha específica.
    fecha_asignada = models.DateField(null=True, blank=True, help_text="Día en que se planea realizar la tarea")
    
    def __str__(self):
        return self.titulo
    
    # Podríamos añadir una meta-clase para ordenar las tareas por defecto, por ejemplo, por fecha_asignada
    class Meta:
        ordering = ['usuario', 'fecha_asignada', 'titulo'] # Añadimos usuario al ordenamiento.
        

class Proyecto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE) # Un proyecto pertenece a un usuario
    nombre = models.CharField(max_length=255, verbose_name="Nombre del Proyecto")
    descripcion = models.TextField(null=True, blank=True, verbose_name="Descripción del Proyecto")

    # Para "tiempo estimado: 1 semana", un CharField es flexible.
    # Si quisieras cálculos más precisos, podrías usar DurationField o campos numéricos.
    # Por ahora, lo mantenemos simple como texto.
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
    fecha_creacion_proyecto = models.DateTimeField(auto_now_add=True) # Fecha de creación del registro del proyecto

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['usuario', 'fecha_fin_estimada', 'nombre']
        verbose_name = "Proyecto" # Nombre singular para el admin
        verbose_name_plural = "Proyectos" # Nombre plural para el admin