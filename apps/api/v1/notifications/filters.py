"""
Filtros de notificaciones.
"""

from django_filters import rest_framework as filters

from apps.api.filters import UserOwnedFilterSet
from apps.notifications.models import Notification


class NotificationFilter(UserOwnedFilterSet):
    leida = filters.BooleanFilter()
    tipo = filters.CharFilter()
    subtipo = filters.CharFilter()
    fecha_creacion = filters.DateFromToRangeFilter()
    fecha_vencimiento = filters.DateFromToRangeFilter()

    class Meta:
        model = Notification
        fields = ("leida", "tipo", "subtipo", "fecha_creacion", "fecha_vencimiento")
        search_fields = ("titulo", "mensaje")


