"""
ViewSets para la API de tareas (v1).
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.api.permissions import IsOwner
from apps.api.v1.tasks.filters import TareaFilter
from apps.api.v1.tasks.serializers import (
    TareaCreateSerializer,
    TareaDetailSerializer,
    TareaListSerializer,
    TareaUpdateSerializer,
)
from apps.projects.models import Proyecto
from apps.tasks.models import Tarea
from apps.tasks.repositories import TareaRepository


@extend_schema_view(
    list=extend_schema(
        summary="Listar tareas del usuario autenticado",
        description="Devuelve las tareas pertenecientes al usuario con filtros, búsqueda y paginación.",
        tags=("Tasks",),
        responses=TareaListSerializer(many=True),
    ),
    retrieve=extend_schema(
        summary="Obtener detalle de una tarea",
        tags=("Tasks",),
        responses=TareaDetailSerializer,
    ),
    create=extend_schema(
        summary="Crear una nueva tarea",
        tags=("Tasks",),
        request=TareaCreateSerializer,
        responses=TareaDetailSerializer,
    ),
    update=extend_schema(
        summary="Actualizar completamente una tarea",
        tags=("Tasks",),
        request=TareaUpdateSerializer,
        responses=TareaDetailSerializer,
    ),
    partial_update=extend_schema(
        summary="Actualizar parcialmente una tarea",
        tags=("Tasks",),
        request=TareaUpdateSerializer,
        responses=TareaDetailSerializer,
    ),
    destroy=extend_schema(
        summary="Eliminar una tarea",
        tags=("Tasks",),
    ),
)
class TareaViewSet(viewsets.ModelViewSet):
    """
    API orientada a recursos que respeta el ownership del usuario.
    """

    queryset = Tarea.objects.none()
    permission_classes = (IsOwner,)
    serializer_class = TareaDetailSerializer
    filterset_class = TareaFilter
    ordering_fields = ("fecha_asignada", "titulo", "fecha_creacion")
    ordering = ("-fecha_asignada", "-fecha_creacion")
    search_fields = ("titulo", "descripcion", "proyecto__nombre")

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Tarea.objects.none()
        return TareaRepository.get_tasks_for_user(user)

    def get_serializer_class(self):
        if self.action == "list":
            return TareaListSerializer
        if self.action == "create":
            return TareaCreateSerializer
        if self.action in {"update", "partial_update"}:
            return TareaUpdateSerializer
        return TareaDetailSerializer

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @extend_schema(summary="Marcar tarea como completada", tags=("Tasks",), responses=TareaDetailSerializer)
    @action(detail=True, methods=["post"], url_path="mark-complete")
    def mark_complete(self, request, *args, **kwargs):
        tarea = self.get_object()
        if tarea.completada:
            return Response(
                {"detail": "La tarea ya está marcada como completada."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tarea.completada = True
        tarea.save(update_fields=["completada", "fecha_modificacion"])
        serializer = TareaDetailSerializer(tarea, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Marcar tarea como pendiente", tags=("Tasks",), responses=TareaDetailSerializer)
    @action(detail=True, methods=["post"], url_path="mark-incomplete")
    def mark_incomplete(self, request, *args, **kwargs):
        tarea = self.get_object()
        if not tarea.completada:
            return Response(
                {"detail": "La tarea ya está marcada como pendiente."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tarea.completada = False
        tarea.save(update_fields=["completada", "fecha_modificacion"])
        serializer = TareaDetailSerializer(tarea, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Asignar o quitar proyecto a una tarea",
        description="Permite asignar un proyecto propiedad del usuario o quitar la asociación.",
        request={
            "application/json": {
                "type": "object",
                "properties": {"project_id": {"type": ["integer", "null"]}},
                "required": [],
            }
        },
        responses={200: TareaDetailSerializer},
        tags=("Tasks",),
    )
    @action(detail=True, methods=["post"], url_path="assign-project")
    def assign_project(self, request, *args, **kwargs):
        tarea = self.get_object()
        project_id = request.data.get("project_id")

        if project_id in (None, "", "null"):
            tarea.proyecto = None
            tarea.save(update_fields=["proyecto", "fecha_modificacion"])
            serializer = TareaDetailSerializer(tarea, context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_200_OK)

        try:
            project_id = int(project_id)
        except (TypeError, ValueError):
            return Response(
                {"detail": "El identificador de proyecto debe ser numérico."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            proyecto = Proyecto.objects.get(id=project_id, usuario=request.user)
        except Proyecto.DoesNotExist:
            return Response(
                {"detail": "Proyecto no encontrado o no te pertenece."},
                status=status.HTTP_404_NOT_FOUND,
            )

        tarea.proyecto = proyecto
        tarea.save(update_fields=["proyecto", "fecha_modificacion"])
        serializer = TareaDetailSerializer(tarea, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_200_OK)


