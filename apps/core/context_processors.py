"""
Context Processors - Datos globales disponibles en todos los templates.

Propósito: Proveer contadores y datos compartidos a nivel de aplicación.
"""

from apps.notifications.models import Notification

def notifications_context(request):
    """
    Provee contador de notificaciones para navbar/header.
    
    Disponible en todos los templates automáticamente como:
    - {{ unread_notifications_count }}
    
    Args:
        request: HttpRequest actual
        
    Returns:
        dict: Context con contador de notificaciones no leídas
    """
    if not request.user.is_authenticated:
        return {'unread_notifications_count': 0}

    unread_count = Notification.objects.filter(
        usuario=request.user,
        leida=False
    ).count()

    return {'unread_notifications_count': unread_count}
