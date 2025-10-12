from django import forms # Importamos el módulo de formularios de Django
from .models import Tarea, Proyecto # Importamos nuestro modelo Tarea y Proyecto
from django.contrib.auth.forms import UserCreationForm # Importamos el UserCreationForm base
from django.contrib.auth.models import User # Importamos el modelo User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML, Div
from allauth.account.forms import LoginForm
from crispy_forms.bootstrap import AppendedText

class TareaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Extract user from kwargs if provided
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter projects to only user's projects
        if self.user:
            self.fields['proyecto'].queryset = Proyecto.objects.filter(usuario=self.user)

    class Meta:
        model = Tarea
        fields = ['titulo', 'descripcion', 'tiempo_estimado', 'fecha_asignada', 'proyecto', 'completada']

        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}), # Añadido
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Añade una descripción detallada...', 'class': 'form-control'}), # Añadido class
            'fecha_asignada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), # Añadido class
            'tiempo_estimado': forms.TextInput(attrs={'placeholder': 'Ej: 1h30m o 0:45:00', 'class': 'form-control'}), # Añadido class
            'completada': forms.CheckboxInput(attrs={'class': 'form-check-input'}), # Para checkboxes
            'proyecto': forms.Select(attrs={'class': 'form-control'}), 
        }
        labels = {
            'titulo': 'Título de la Tarea',
            'descripcion': 'Descripción Detallada',
            'tiempo_estimado': 'Tiempo Estimado (ej: 2h, 45m)',
            'fecha_asignada': 'Fecha Asignada',
            'completada': '¿Está Completada?',
            'proyecto': 'Proyecto (Opcional)',
        }
        help_texts = {
            'tiempo_estimado': 'Usa un formato como "1h 30m", "00:30:00".',
            'proyecto': 'Selecciona el proyecto para organizar esta tarea (opcional).',
        }



class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Requerido. Se necesita una dirección de correo válida.')
    first_name = forms.CharField(max_length=100, required=True, label='Nombre', help_text='Requerido.')
    last_name = forms.CharField(max_length=100, required=False, label='Apellido')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # ... tu layout ...
        self.helper.layout = Layout(
            'username',
            'first_name',
            'last_name',
            'email',
            AppendedText('password', '<button class="btn btn-outline-secondary toggle-password" type="button">👁️ Ver</button>'),
            AppendedText('password2', '<button class="btn btn-outline-secondary toggle-password" type="button">👁️ Ver</button>')
        )

    # --- MÉTODO SAVE (ESENCIAL) ---
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.email = self.cleaned_data["email"]
        if self.cleaned_data.get("last_name"):
            user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class CustomLoginForm(LoginForm):
    # Definimos explícitamente los campos que queremos
    login = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'placeholder': 'tucorreo@mail.com'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
    )
    remember = forms.BooleanField(label="Recordarme", required=False)
        
    
class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion', 'tiempo_estimado_general', 'fecha_inicio', 'fecha_fin_estimada', 'estado']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'tiempo_estimado_general': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin_estimada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        }

        labels = {
            'nombre': 'Nombre del Proyecto',
            'descripcion': 'Descripción Detallada del Proyecto',
            'tiempo_estimado_general': 'Tiempo Estimado General',
            'fecha_inicio': 'Fecha de Inicio del Proyecto',
            'fecha_fin_estimada': 'Fecha Estimada de Finalización',
            'estado': 'Estado Actual del Proyecto',
        }
        

class TareaEstadoForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['completada'] # Solo nos interesa este campo