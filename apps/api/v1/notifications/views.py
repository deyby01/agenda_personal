"""
ViewSets para notificaciones.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.api.permissions import IsOwner
from apps.api.v1.notifications.filters import NotificationFilter
from apps.api.v1.notifications.serializers import (
    BaseNotificationSerializer,
    NotificationBulkActionSerializer,
    NotificationCreateSerializer,
    NotificationDetailSerializer,
    NotificationListSerializer,
    NotificationUpdateSerializer,
)
from apps.notifications.models import Notification
from apps.notifications.repositories import NotificationRepository


@extend_schema_view(
    list=extend_schema(
        summary="Listar notificaciones del usuario",
        tags=("Notifications",),
        responses=NotificationListSerializer(many=True),
    ),
    retrieve=extend_schema(
        summary="Detalle de una notificación",
        tags=("Notifications",),
        responses=NotificationDetailSerializer,
    ),
    create=extend_schema(
        summary="Crear una notificación",
        tags=("Notifications",),
        request=NotificationCreateSerializer,
        responses=NotificationDetailSerializer,
    ),
    update=extend_schema(
        summary="Actualizar una notificación",
        tags=("Notifications",),
        request=NotificationUpdateSerializer,
        responses=NotificationDetailSerializer,
    ),
    partial_update=extend_schema(
        summary="Actualizar parcialmente una notificación",
        tags=("Notifications",),
        request=NotificationUpdateSerializer,
        responses=NotificationDetailSerializer,
    ),
    destroy=extend_schema(
        summary="Eliminar una notificación",
        tags=("Notifications",),
    ),
)
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.none()
    permission_classes = (IsOwner,)
    serializer_class = BaseNotificationSerializer
    filterset_class = NotificationFilter
    ordering_fields = ("fecha_creacion", "tipo", "subtipo")
    ordering = ("-fecha_creacion",)
    search_fields = ("titulo", "mensaje")

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Notification.objects.none()
        return NotificationRepository.get_all_for_user(user)

    def get_serializer_class(self):
        if self.action == "list":
            return NotificationListSerializer
        if self.action == "create":
            return NotificationCreateSerializer
        if self.action in {"update", "partial_update"}:
            return NotificationUpdateSerializer
        return NotificationDetailSerializer

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @extend_schema(
        summary="Marcar notificación como leída",
        tags=("Notifications",),
        responses={200: NotificationDetailSerializer},
    )
    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, *args, **kwargs):
        notification = self.get_object()
        if notification.leida:
            return Response({"detail": "La notificación ya estaba leída."}, status=status.HTTP_200_OK)

        notification.mark_as_read()
        serializer = NotificationDetailSerializer(notification, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Marcar notificación como atendida",
        tags=("Notifications",),
        responses={200: NotificationDetailSerializer},
    )
    @action(detail=True, methods=["post"], url_path="mark-actioned")
    def mark_actioned(self, request, *args, **kwargs):
        notification = self.get_object()
        if notification.accionada:
            return Response({"detail": "La notificación ya estaba accionada."}, status=status.HTTP_200_OK)

        notification.mark_as_actioned()
        serializer = NotificationDetailSerializer(notification, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Marcar múltiples notificaciones como leídas",
        request=NotificationBulkActionSerializer,
        responses={200: {"type": "object", "properties": {"updated": {"type": "integer"}}}},
        tags=("Notifications",),
    )
    @action(detail=False, methods=["post"], url_path="bulk-mark-read")
    def bulk_mark_read(self, request, *args, **kwargs):
        serializer = NotificationBulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        notifications = Notification.objects.filter(
            id__in=serializer.validated_data["notification_ids"],
            usuario=request.user,
            leida=False,
        )
        updated = notifications.update(leida=True)
        return Response({"updated": updated}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Marcar todas las notificaciones como leídas",
        responses={200: {"type": "object", "properties": {"updated": {"type": "integer"}}}},
        tags=("Notifications",),
    )
    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request, *args, **kwargs):
        updated = NotificationRepository.mark_all_as_read(request.user)
        return Response({"updated": updated}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Contar notificaciones no leídas",
        responses={200: {"type": "object", "properties": {"unread": {"type": "integer"}}}},
        tags=("Notifications",),
    )
    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request, *args, **kwargs):
        count = NotificationRepository.get_unread_count(request.user)
        return Response({"unread": count}, status=status.HTTP_200_OK)
