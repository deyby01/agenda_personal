"""
Context Processors para datos globales de templates

Proposito: Proveer contador de notificaciones a todos los templates
"""
from .models import Notification

def notifications_context(request):
    """
    Provee contador de notificaciones para navbar
    Disponible en todos los templates automaticamente
    """
    if not request.user.is_authenticated:
        return {'unread_notifications_count': 0}

    # Contar notificaciones no leidas del usuario
    unread_count = Notification.objects.filter(
        usuario=request.user,
        leida=False
    ).count()

    return {'unread_notifications_count': unread_count}