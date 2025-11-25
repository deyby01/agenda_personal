"""
Serializers para la API de tareas (v1).
"""

from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from apps.projects.models import Proyecto
from apps.tasks.models import Tarea


class ProjectSummarySerializer(serializers.ModelSerializer):
    """
    Resumen ligero del proyecto asociado.
    """

    class Meta:
        model = Proyecto
        fields = ("id", "nombre", "estado", "fecha_fin_estimada")


class BaseTareaSerializer(serializers.ModelSerializer):
    """
    Serializer base que encapsula validaciones compartidas.
    """

    class Meta:
        model = Tarea
        fields = (
            "id",
            "titulo",
            "descripcion",
            "completada",
            "tiempo_estimado",
            "fecha_asignada",
            "proyecto",
            "usuario",
            "fecha_creacion",
            "fecha_modificacion",
        )
        read_only_fields = ("id", "usuario", "fecha_creacion", "fecha_modificacion")

    def validate_proyecto(self, value):
        """
        Garantiza que solo se puedan asignar proyectos del mismo usuario.
        """

        if value is None:
            return value

        request = self.context.get("request")
        if request and value.usuario != request.user:
            raise serializers.ValidationError("Solo puedes usar proyectos que te pertenecen.")
        return value

    def validate_fecha_asignada(self, value):
        """
        Evita fechas excesivamente antiguas para mantener consistencia.
        """

        if value and value < timezone.localdate() - timedelta(days=365 * 5):
            raise serializers.ValidationError("La fecha asignada no puede ser tan antigua.")
        return value


class TareaListSerializer(BaseTareaSerializer):
    project_name = serializers.CharField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta(BaseTareaSerializer.Meta):
        fields = (
            "id",
            "titulo",
            "completada",
            "fecha_asignada",
            "proyecto",
            "project_name",
            "is_overdue",
        )


class TareaDetailSerializer(BaseTareaSerializer):
    project_name = serializers.CharField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    proyecto_detalle = ProjectSummarySerializer(source="proyecto", read_only=True)

    class Meta(BaseTareaSerializer.Meta):
        fields = BaseTareaSerializer.Meta.fields + (
            "project_name",
            "is_overdue",
            "proyecto_detalle",
        )


class TareaCreateSerializer(BaseTareaSerializer):
    class Meta(BaseTareaSerializer.Meta):
        extra_kwargs = {
            "completada": {"required": False},
            "proyecto": {"required": False, "allow_null": True},
            "fecha_asignada": {"required": False, "allow_null": True},
        }

    def create(self, validated_data):
        validated_data["usuario"] = self.context["request"].user
        return super().create(validated_data)


class TareaUpdateSerializer(BaseTareaSerializer):
    class Meta(BaseTareaSerializer.Meta):
        extra_kwargs = {
            "proyecto": {"required": False, "allow_null": True},
            "fecha_asignada": {"required": False, "allow_null": True},
        }


