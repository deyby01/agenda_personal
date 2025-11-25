"""
Filtros de proyectos.
"""

from django_filters import rest_framework as filters

from apps.api.filters import UserOwnedFilterSet
from apps.projects.models import Proyecto


class ProyectoFilter(UserOwnedFilterSet):
    """
    Filtros para proyectos con soporte de rangos de fechas.
    """

    estado = filters.CharFilter()
    fecha_inicio = filters.DateFromToRangeFilter()
    fecha_fin_estimada = filters.DateFromToRangeFilter()

    class Meta:
        model = Proyecto
        fields = ("estado", "fecha_inicio", "fecha_fin_estimada")
        search_fields = ("nombre", "descripcion")


