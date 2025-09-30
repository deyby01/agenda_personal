from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Tarea, Proyecto

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class TareaSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)
    class Meta:
        model = Tarea
        fields = ['id', 'titulo', 'descripcion', 'fecha_creacion', 'completada', 'tiempo_estimado', 'fecha_asignada', 'usuario']


class ProyectoSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)
    class Meta:
        model = Proyecto
        fields = ['id', 'nombre', 'descripcion', 'tiempo_estimado_general', 'fecha_inicio', 'fecha_fin_estimada', 'estado', 'fecha_creacion_proyecto', 'usuario']