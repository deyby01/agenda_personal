"""
Manejo centralizado de excepciones para la API.

Ofrece helpers reutilizables y respeta SOLID separando responsabilidades.
"""

import logging
from typing import Any, Dict, Optional

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)

class ApiError(APIException):
    """
    Excepción base para la API con payload consistente.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Se produjo un error al procesar la solicitud."
    default_code = "api_error"

    def __init__(
        self,
        detail: Any = None,
        *,
        code: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
    ) -> None:
        if status_code:
            self.status_code = status_code
        self.extra = extra or {}
        super().__init__(detail=detail, code=code)


class DomainValidationError(ApiError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "La solicitud no cumple las reglas de negocio."
    default_code = "domain_validation_error"


class ResourceNotFoundError(ApiError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "El recurso solicitado no existe."
    default_code = "resource_not_found"


def _build_payload(
    detail: Any,
    *,
    code: str = "error",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "success": False,
        "code": code,
        "detail": detail,
    }
    if extra:
        payload["extra"] = extra
    return payload


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Response:
    """
    Envoltorio sobre el handler de DRF para entregar respuestas consistentes.
    """

    response = drf_exception_handler(exc, context)

    if response is not None:
        detail = response.data
        code = "error"

        if isinstance(exc, APIException):
            code = getattr(exc, "default_code", code)
            if isinstance(response.data, dict) and "detail" in response.data:
                detail = response.data["detail"]

        response.data = _build_payload(detail, code=code)
        return response

    if isinstance(exc, ApiError):
        logger.exception("API error captured", exc_info=exc)
        return Response(
            _build_payload(exc.detail, code=exc.default_code, extra=getattr(exc, "extra", None)),
            status=exc.status_code,
        )

    logger.exception("Unhandled exception in API", exc_info=exc)
    return Response(
        _build_payload("Error interno inesperado", code="internal_error"),
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


