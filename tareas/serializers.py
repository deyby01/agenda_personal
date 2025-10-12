from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Tarea, Proyecto

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class ProyectoLightSerializer(serializers.ModelSerializer):
    """ Lightweight project serializer for nested relationships """
    class Meta:
        model = Proyecto
        fields = ['id', 'nombre', 'estado']


class TareaSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)
    proyecto = ProyectoLightSerializer(read_only=True)
    proyecto_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Tarea
        fields = ['id', 'titulo', 'descripcion', 'fecha_creacion', 'completada', 'tiempo_estimado', 'fecha_asignada', 'usuario', 'proyecto', 'proyecto_id']

    def validate_proyecto_id(self, value):
        """
        Validate that project belongs to user.
        """
        if value is not None:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                try:
                    proyecto = Proyecto.objects.get(id=value, usuario=request.user)
                    return value
                except Proyecto.DoesNotExist:
                    raise serializers.ValidationError("Proyecto no encontrado, o no tienes permisos.")


class ProyectoSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)
    completion_percentage = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Proyecto
        fields = ['id', 'nombre', 'descripcion', 'tiempo_estimado_general', 'fecha_inicio', 
                    'fecha_fin_estimada', 'estado', 'fecha_creacion_proyecto', 'usuario',
                    'completion_percentage', 'task_count']

    def get_completion_percentage(self, obj):
        """
        Get project completion percentage.
        """
        return obj.get_completion_percentage()

    def get_task_count(self, obj):
        """
        Get project task count.
        """
        return obj.tareas.count()