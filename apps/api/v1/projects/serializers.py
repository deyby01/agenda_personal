"""
Serializers para proyectos.
"""

from rest_framework import serializers

from apps.projects.models import Proyecto
from apps.tasks.models import Tarea


class ProyectoTaskSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarea
        fields = ("id", "titulo", "completada", "fecha_asignada")


class BaseProyectoSerializer(serializers.ModelSerializer):
    completion_percentage = serializers.FloatField(source="get_completion_percentage", read_only=True)
    total_tareas = serializers.IntegerField(read_only=True)
    tareas_completadas = serializers.IntegerField(read_only=True)
    tareas_pendientes = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Proyecto
        fields = (
            "id",
            "nombre",
            "descripcion",
            "estado",
            "fecha_inicio",
            "fecha_fin_estimada",
            "tiempo_estimado_general",
            "usuario",
            "fecha_creacion",
            "fecha_modificacion",
            "completion_percentage",
            "total_tareas",
            "tareas_completadas",
            "tareas_pendientes",
            "is_active",
        )
        read_only_fields = ("id", "usuario", "fecha_creacion", "fecha_modificacion")


class ProyectoListSerializer(BaseProyectoSerializer):
    class Meta(BaseProyectoSerializer.Meta):
        fields = (
            "id",
            "nombre",
            "estado",
            "fecha_inicio",
            "fecha_fin_estimada",
            "completion_percentage",
            "total_tareas",
            "tareas_pendientes",
            "is_active",
        )


class ProyectoDetailSerializer(BaseProyectoSerializer):
    tareas_resumen = serializers.SerializerMethodField()

    class Meta(BaseProyectoSerializer.Meta):
        fields = BaseProyectoSerializer.Meta.fields + ("tareas_resumen",)

    def get_tareas_resumen(self, obj):
        tareas = obj.tareas.order_by("-fecha_asignada")[:10]
        return ProyectoTaskSummarySerializer(tareas, many=True).data


class ProyectoCreateSerializer(BaseProyectoSerializer):
    class Meta(BaseProyectoSerializer.Meta):
        extra_kwargs = {
            "fecha_inicio": {"required": False, "allow_null": True},
            "fecha_fin_estimada": {"required": False, "allow_null": True},
            "tiempo_estimado_general": {"required": False, "allow_null": True},
            "descripcion": {"required": False, "allow_blank": True},
        }

    def create(self, validated_data):
        validated_data["usuario"] = self.context["request"].user
        return super().create(validated_data)


class ProyectoUpdateSerializer(BaseProyectoSerializer):
    class Meta(BaseProyectoSerializer.Meta):
        extra_kwargs = {
            "fecha_inicio": {"required": False, "allow_null": True},
            "fecha_fin_estimada": {"required": False, "allow_null": True},
            "descripcion": {"required": False, "allow_blank": True},
            "tiempo_estimado_general": {"required": False, "allow_null": True},
        }


class ProyectoStatsSerializer(serializers.Serializer):
    total_tareas = serializers.IntegerField()
    tareas_completadas = serializers.IntegerField()
    tareas_pendientes = serializers.IntegerField()
    completion_percentage = serializers.FloatField()


class ProyectoStatsPayloadSerializer(serializers.Serializer):
    project = ProyectoDetailSerializer()
    stats = ProyectoStatsSerializer()

    def to_representation(self, instance):
        project = instance.get("project")
        stats = instance.get("stats")
        project_data = ProyectoDetailSerializer(project, context=self.context).data
        stats_data = ProyectoStatsSerializer(stats).data
        return {
            "project": project_data,
            "stats": stats_data,
        }



