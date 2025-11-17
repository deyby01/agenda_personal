"""
Project Forms - Form layer para Projects domain.

Migrado desde tareas/forms.py con mejoras:
- Imports actualizados
- Organización por dominio
- Validación robusta
"""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML, Div

from apps.projects.models import Proyecto


class ProyectoForm(forms.ModelForm):
    """
    Form para crear y editar proyectos.
    
    Features:
    - Widgets personalizados
    - Validación de fechas
    - Help texts informativos
    
    Usage:
        form = ProyectoForm(instance=proyecto)
    """
    
    class Meta:
        model = Proyecto
        fields = [
            'nombre',
            'descripcion',
            'estado',
            'fecha_inicio',
            'fecha_fin_estimada',
            'tiempo_estimado_general'
        ]

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del proyecto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del proyecto'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_fin_estimada': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'tiempo_estimado_general': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 40 horas'
            }),
        }
        
        labels = {
            'nombre': 'Nombre del Proyecto',
            'descripcion': 'Descripción',
            'estado': 'Estado',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin_estimada': 'Fecha de Fin Estimada',
            'tiempo_estimado_general': 'Tiempo Estimado Total',
        }
    
    def clean(self):
        """
        Validación personalizada del formulario.
        
        Verifica que fecha_fin_estimada >= fecha_inicio.
        
        Returns:
            dict: Cleaned data
            
        Raises:
            ValidationError: Si las fechas son inconsistentes
        """
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin_estimada = cleaned_data.get('fecha_fin_estimada')
        
        if fecha_inicio and fecha_fin_estimada:
            if fecha_fin_estimada < fecha_inicio:
                raise forms.ValidationError(
                    "La fecha de fin estimada no puede ser anterior a la fecha de inicio."
                )
        
        return cleaned_data
