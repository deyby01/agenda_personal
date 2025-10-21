"""
Core views - Shared functionality
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_GET
def health_check(request):
    """
    Health check endpoint para Docker y monitoreo
    
    Returns:
        JSON: Status y información del servicio
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'agenda-enterprise',
        'version': '2.0.0',
        'apps': [
            'core', 'tasks', 'projects', 
            'notifications', 'api'
        ],
        'environment': 'docker'
    })