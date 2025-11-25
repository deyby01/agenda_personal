"""
Serializers para notificaciones.
"""

from rest_framework import serializers

from apps.notifications.models import Notification
from apps.projects.models import Proyecto
from apps.tasks.models import Tarea


class NotificationTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarea
        fields = ("id", "titulo", "completada")


class NotificationProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = ("id", "nombre", "estado")


class BaseNotificationSerializer(serializers.ModelSerializer):
    urgency_icon = serializers.CharField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    requires_action = serializers.BooleanField(read_only=True)
    tarea_resumen = NotificationTaskSerializer(source="tarea_relacionada", read_only=True)
    proyecto_resumen = NotificationProjectSerializer(source="proyecto_relacionado", read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id",
            "titulo",
            "mensaje",
            "tipo",
            "subtipo",
            "leida",
            "accionada",
            "usuario",
            "tarea_relacionada",
            "proyecto_relacionado",
            "tarea_resumen",
            "proyecto_resumen",
            "fecha_vencimiento",
            "business_context",
            "fecha_creacion",
            "fecha_modificacion",
            "urgency_icon",
            "is_expired",
            "requires_action",
        )
        read_only_fields = ("id", "fecha_creacion", "fecha_modificacion", "usuario")


class NotificationListSerializer(BaseNotificationSerializer):
    class Meta(BaseNotificationSerializer.Meta):
        fields = (
            "id",
            "titulo",
            "mensaje",
            "tipo",
            "subtipo",
            "leida",
            "accionada",
            "urgency_icon",
            "requires_action",
            "fecha_creacion",
        )


class NotificationDetailSerializer(BaseNotificationSerializer):
    class Meta(BaseNotificationSerializer.Meta):
        fields = BaseNotificationSerializer.Meta.fields


class NotificationCreateSerializer(BaseNotificationSerializer):
    class Meta(BaseNotificationSerializer.Meta):
        extra_kwargs = {
            "tarea_relacionada": {"required": False, "allow_null": True},
            "proyecto_relacionado": {"required": False, "allow_null": True},
            "business_context": {"required": False, "allow_null": True},
            "fecha_vencimiento": {"required": False, "allow_null": True},
        }

    def create(self, validated_data):
        validated_data["usuario"] = self.context["request"].user
        return super().create(validated_data)


class NotificationUpdateSerializer(BaseNotificationSerializer):
    class Meta(BaseNotificationSerializer.Meta):
        extra_kwargs = {
            "tarea_relacionada": {"required": False, "allow_null": True},
            "proyecto_relacionado": {"required": False, "allow_null": True},
            "business_context": {"required": False, "allow_null": True},
            "fecha_vencimiento": {"required": False, "allow_null": True},
        }


class NotificationBulkActionSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        help_text="IDs de notificaciones a actualizar",
    )
