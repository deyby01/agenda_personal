"""
Filtros específicos para tareas.
"""

from django_filters import rest_framework as filters

from apps.api.filters import UserOwnedFilterSet
from apps.tasks.models import Tarea


class TareaFilter(UserOwnedFilterSet):
    """
    Filtros para búsqueda avanzada de tareas.
    """

    completada = filters.BooleanFilter()
    proyecto = filters.NumberFilter(field_name="proyecto_id")
    fecha_asignada = filters.DateFromToRangeFilter()

    class Meta:
        model = Tarea
        fields = ("completada", "proyecto", "fecha_asignada")
        search_fields = ("titulo", "descripcion")


