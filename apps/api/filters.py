"""
Filtros compartidos para la API.
"""

from functools import cached_property
from typing import Any, Dict

from django_filters import rest_framework as filters


class SearchFilterMixin:
    """
    Mixin que agrega búsqueda básica por campos definidos en Meta.search_fields.
    """

    search = filters.CharFilter(method="filter_search")

    def filter_search(self, queryset, name, value):  # type: ignore[override]
        if not value:
            return queryset

        search_fields = getattr(self.Meta, "search_fields", [])  # type: ignore[attr-defined]
        if not search_fields:
            return queryset

        query = filters.Q()
        for field in search_fields:
            query |= filters.Q(**{f"{field}__icontains": value})
        return queryset.filter(query)


class UserOwnedFilterSet(SearchFilterMixin, filters.FilterSet):
    """
    FilterSet base que garantiza que los resultados pertenezcan al usuario autenticado.
    """

    owner_field = "usuario"

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        self._request = request
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)

    @cached_property
    def _owner_lookup(self) -> Dict[str, Any]:
        owner_field = getattr(self.Meta, "owner_field", self.owner_field)  # type: ignore[attr-defined]
        return {owner_field: getattr(self._request, "user", None)}

    @property
    def qs(self):  # type: ignore[override]
        queryset = super().qs
        user = getattr(self._request, "user", None)

        if not user or not user.is_authenticated:
            return queryset.none()

        owner_lookup = self._owner_lookup
        if owner_lookup.get(next(iter(owner_lookup))) is None:
            owner_lookup[next(iter(owner_lookup))] = user

        return queryset.filter(**owner_lookup)


