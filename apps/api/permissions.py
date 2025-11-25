"""
Permisos personalizados para la API.

Se enfocan en ownership y lectura segura, respetando SRP.
"""

from typing import Any

from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.views import View


class IsOwner(BasePermission):
    """
    Permite acceso solo a recursos pertenecientes al usuario autenticado.

    Se asume que el modelo expone un atributo `usuario` o `user`.
    """

    message = "Solo puedes acceder a recursos que te pertenecen."

    def has_permission(self, request: Request, view: View) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(
        self,
        request: Request,
        view: View,
        obj: Any,
    ) -> bool:
        owner = getattr(obj, "usuario", None) or getattr(obj, "user", None)
        return owner == request.user


class IsOwnerOrReadOnly(IsOwner):
    """
    Permite lectura a cualquiera autenticado, escritura solo al owner.
    """

    message = "Solo el propietario puede modificar este recurso."

    def has_object_permission(
        self,
        request: Request,
        view: View,
        obj: Any,
    ) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return super().has_object_permission(request, view, obj)


