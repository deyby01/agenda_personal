from django.contrib import admin
from apps.projects.models import Proyecto


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    """Admin configuration for Proyecto"""
    
    list_display = (
        'nombre',
        'usuario',
        'estado',
        'fecha_inicio',
        'fecha_fin_estimada',
        'get_completion_display'
    )
    list_filter = ('estado', 'fecha_inicio', 'usuario')
    search_fields = ('nombre', 'descripcion', 'usuario__username')
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'usuario', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin_estimada', 'tiempo_estimado_general')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_completion_display(self, obj):
        """Muestra % de completación en admin"""
        return f"{obj.get_completion_percentage()}%"
    get_completion_display.short_description = 'Completado'
