"""
Task Forms - Form layer para Tasks domain.

Migrado desde tareas/forms.py con mejoras:
- Imports actualizados a nueva arquitectura
- Mejor organización
- Docstrings completos
"""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML, Div
from crispy_forms.bootstrap import AppendedText

from apps.tasks.models import Tarea
from apps.projects.models import Proyecto


class TareaForm(forms.ModelForm):
    """
    Form para crear y editar tareas.
    
    Features:
    - Filtra proyectos por usuario
    - Widgets personalizados con Crispy Forms
    - Validación automática de campos
    
    Usage:
        form = TareaForm(user=request.user, instance=tarea)
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor personalizado.

        Args:
            user: Usuario actual (para filtrar proyectos)
        """

        # Extraer user de kwargs si esta presente
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filtrar proyectos solo del usuario
        if self.user:
            self.fields['proyecto'].queryset = Proyecto.objects.filter(usuario=self.user)

    class Meta:
        model = Tarea
        fields = [
            'titulo',
            'descripcion',
            'tiempo_estimado',
            'fecha_asignada',
            'proyecto',
            'completada'
        ]

        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la tarea'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada (Opcional)'
            }),
            'tiempo_estimado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '2:30:00 (HH:MM:SS)'
            }),
            'fecha_asignada': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'proyecto': forms.Select(attrs={
                'class': 'form-control',
            }),
            'completada': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'tiempo_estimado': 'Tiempo estimado',
            'fecha_asignada': 'Fecha asignada',
            'proyecto': 'Proyecto (Opcional)',
            'completada': '¿Completada?'
        }


class TareaEstadoForm(forms.ModelForm):
    """
    Form simple para cambiar el estado de completada de una tarea.
    
    Usado para toggle rápido del estado sin editar toda la tarea.
    
    Usage:
        form = TareaEstadoForm(instance=tarea)
        form.save()
    """
    
    class Meta:
        model = Tarea
        fields = ['completada']