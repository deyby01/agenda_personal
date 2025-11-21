from django.contrib import admin
from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification"""
    
    list_display = (
        'urgency_icon_display',
        'titulo',
        'usuario',
        'tipo',
        'subtipo',
        'leida',
        'accionada',
        'fecha_creacion'
    )
    list_filter = ('tipo', 'subtipo', 'leida', 'accionada', 'fecha_creacion')
    search_fields = ('titulo', 'mensaje', 'usuario__username')
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'urgency_icon')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'mensaje', 'usuario')
        }),
        ('Clasificación', {
            'fields': ('tipo', 'subtipo')
        }),
        ('Estado', {
            'fields': ('leida', 'accionada')
        }),
        ('Relaciones', {
            'fields': ('tarea_relacionada', 'proyecto_relacionado')
        }),
        ('Contexto', {
            'fields': ('business_context', 'fecha_vencimiento'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    def urgency_icon_display(self, obj):
        """Muestra ícono de urgencia en admin"""
        return obj.urgency_icon
    urgency_icon_display.short_description = 'Urgencia'
    
    actions = ['mark_selected_as_read']
    
    def mark_selected_as_read(self, request, queryset):
        """Acción masiva: marcar como leídas"""
        updated = queryset.update(leida=True)
        self.message_user(request, f'{updated} notificaciones marcadas como leídas.')
    mark_selected_as_read.short_description = 'Marcar como leídas'
