"""
ViewSets para proyectos.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.api.permissions import IsOwner
from apps.api.v1.projects.filters import ProyectoFilter
from apps.api.v1.projects.serializers import (
    ProyectoCreateSerializer,
    ProyectoDetailSerializer,
    ProyectoListSerializer,
    ProyectoStatsPayloadSerializer,
    ProyectoStatsSerializer,
    ProyectoUpdateSerializer,
)
from apps.api.v1.tasks.serializers import TareaListSerializer
from apps.projects.models import Proyecto
from apps.projects.repositories import ProyectoRepository


@extend_schema_view(
    list=extend_schema(
        summary="Listar proyectos del usuario",
        description="Incluye métricas resumidas (tareas totales, completadas, pendientes).",
        tags=("Projects",),
        responses=ProyectoListSerializer(many=True),
    ),
    retrieve=extend_schema(
        summary="Detalle de un proyecto",
        tags=("Projects",),
        responses=ProyectoDetailSerializer,
    ),
    create=extend_schema(
        summary="Crear un proyecto",
        tags=("Projects",),
        request=ProyectoCreateSerializer,
        responses=ProyectoDetailSerializer,
    ),
    update=extend_schema(
        summary="Actualizar un proyecto",
        tags=("Projects",),
        request=ProyectoUpdateSerializer,
        responses=ProyectoDetailSerializer,
    ),
    partial_update=extend_schema(
        summary="Actualizar parcialmente un proyecto",
        tags=("Projects",),
        request=ProyectoUpdateSerializer,
        responses=ProyectoDetailSerializer,
    ),
    destroy=extend_schema(
        summary="Eliminar un proyecto",
        tags=("Projects",),
    ),
)
class ProyectoViewSet(viewsets.ModelViewSet):
    queryset = Proyecto.objects.none()
    permission_classes = (IsOwner,)
    serializer_class = ProyectoDetailSerializer
    filterset_class = ProyectoFilter
    ordering_fields = ("fecha_fin_estimada", "nombre", "fecha_creacion")
    ordering = ("fecha_fin_estimada",)
    search_fields = ("nombre", "descripcion")

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Proyecto.objects.none()
        return ProyectoRepository.get_all_projects_for_user(user).select_related("usuario")

    def get_serializer_class(self):
        if self.action == "list":
            return ProyectoListSerializer
        if self.action == "create":
            return ProyectoCreateSerializer
        if self.action in {"update", "partial_update"}:
            return ProyectoUpdateSerializer
        return ProyectoDetailSerializer

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @extend_schema(
        summary="Obtener estadísticas del proyecto",
        tags=("Projects",),
        responses={200: ProyectoStatsPayloadSerializer},
    )
    @action(detail=True, methods=["get"], url_path="stats")
    def stats(self, request, *args, **kwargs):
        proyecto = self.get_object()
        data = ProyectoRepository.get_project_with_tasks_stats(proyecto.id, request.user)
        if not data:
            return Response({"detail": "Proyecto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProyectoDetailSerializer(proyecto, context=self.get_serializer_context())
        stats_payload = {
            "project": proyecto,
            "stats": data,
        }
        envelope = ProyectoStatsPayloadSerializer(
            stats_payload, context=self.get_serializer_context()
        )
        return Response(envelope.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Listar tareas del proyecto",
        description="Devuelve las tareas asociadas respetando filtros globales de la vista.",
        tags=("Projects", "Tasks"),
        responses={200: TareaListSerializer(many=True)},
    )
    @action(detail=True, methods=["get"], url_path="tasks")
    def tasks(self, request, *args, **kwargs):
        proyecto = self.get_object()
        tareas = proyecto.tareas.select_related("proyecto").order_by("-fecha_asignada")

        page = self.paginate_queryset(tareas)
        serializer = TareaListSerializer(page or tareas, many=True, context=self.get_serializer_context())

        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Cambiar el estado del proyecto",
        request={
            "application/json": {
                "type": "object",
                "properties": {"estado": {"type": "string"}},
                "required": ["estado"],
            }
        },
        responses={200: ProyectoDetailSerializer},
        tags=("Projects",),
    )
    @action(detail=True, methods=["post"], url_path="change-status")
    def change_status(self, request, *args, **kwargs):
        proyecto = self.get_object()
        nuevo_estado = request.data.get("estado")
        valid_states = [choice[0] for choice in Proyecto.ESTADO_CHOICES]

        if nuevo_estado not in valid_states:
            return Response(
                {"detail": f"Estado inválido. Valores permitidos: {', '.join(valid_states)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        proyecto.estado = nuevo_estado
        proyecto.save(update_fields=["estado", "fecha_modificacion"])
        serializer = ProyectoDetailSerializer(proyecto, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_200_OK)
