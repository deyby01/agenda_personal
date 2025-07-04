from django import forms # Importamos el módulo de formularios de Django
from .models import Tarea, Proyecto # Importamos nuestro modelo Tarea y Proyecto
from django.contrib.auth.forms import UserCreationForm # Importamos el UserCreationForm base
from django.contrib.auth.models import User # Importamos el modelo User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML, Row, Column, Div

class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['titulo', 'descripcion', 'tiempo_estimado', 'fecha_asignada', 'completada']

        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}), # Añadido
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Añade una descripción detallada...', 'class': 'form-control'}), # Añadido class
            'fecha_asignada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), # Añadido class
            'tiempo_estimado': forms.TextInput(attrs={'placeholder': 'Ej: 1h30m o 0:45:00', 'class': 'form-control'}), # Añadido class
            'completada': forms.CheckboxInput(attrs={'class': 'form-check-input'}), # Para checkboxes
        }
        labels = {
            'titulo': 'Título de la Tarea',
            'descripcion': 'Descripción Detallada',
            'tiempo_estimado': 'Tiempo Estimado (ej: 2h, 45m)',
            'fecha_asignada': 'Fecha Asignada',
            'completada': '¿Está Completada?',
        }
        help_texts = {
            'tiempo_estimado': 'Usa un formato como "1h 30m", "00:30:00". Django intentará interpretarlo.',
        }



class CustomUserCreationForm(UserCreationForm):
    # Añadimos los campos que queremos: email y first_name
    # El campo 'email' en el modelo User es obligatorio por defecto en algunas configuraciones,
    # así que es bueno incluirlo y hacerlo requerido.
    email = forms.EmailField(required=True, help_text='Requerido. Se necesita una dirección de correo válida.')
    first_name = forms.CharField(max_length=100, required=True, label='Nombre', help_text='Requerido.')
    last_name = forms.CharField(max_length=100, required=False, label='Apellido') # Opcional si lo quieres

    class Meta(UserCreationForm.Meta):
        # Heredamos de la Meta clase de UserCreationForm
        model = User # Nos aseguramos de que el modelo sea el User de Django
        # Incluimos los campos originales de UserCreationForm (username, password1, password2)
        # y añadimos los nuestros. El orden aquí definirá el orden en el formulario.
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email') # Si añadiste last_name, ponlo aquí también
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        # No necesitamos un botón de submit aquí si ya lo tenemos en la plantilla HTML
        # self.helper.add_input(Submit('submit', 'Registrarse', css_class='btn-primary'))
        
        # Definimos el layout del formulario
        self.helper.layout = Layout(
            # UserCreationForm tiene 'username', luego muestro 'first_name', 'last_name' y 'email'
            ## y luego 'password1', 'password2' (que se llaman new_password1 y new_password2 internamente)
            'username',
            'first_name',
            'last_name',
            'email',
            # Para los campos de contraseña, usaremos un Div para envolver el input-group
            # Accedemos a los campos de contraseña que UserCreationForm define: new_password1 y new_password2
            Div(
                Field('new_password1', wrapper_class='mb-0'), # mb-0 para el Field para que el input-group maneje el margen
                HTML("""
                    <button class="btn btn-outline-secondary toggle-password" type="button" 
                            data-target="{{ form.new_password1.id_for_label }}">👁️ Ver</button>
                """),
                css_class='input-group mb-3' # mb-3 para el input-group
            ),
            Div(
                Field('new_password2', wrapper_class='mb-0'),
                HTML("""
                    <button class="btn btn-outline-secondary toggle-password" type="button" 
                            data-target="{{ form.new_password2.id_for_label }}">👁️ Ver</button>
                """),
                css_class='input-group mb-3'
            ),
            # Si tuvieras otros campos, los añadirías aquí
        )
        # Si no quieres que Crispy renderice el <form> y {% csrf_token %} (porque ya lo tienes en la plantilla)
        # self.helper.form_tag = False # Descomenta si es necesario

    def save(self, commit=True):
        # Sobrescribimos el método save para guardar también los campos adicionales.
        user = super().save(commit=False) # Llama al save() del padre (UserCreationForm) sin guardar en BD aún
        user.first_name = self.cleaned_data["first_name"]
        user.email = self.cleaned_data["email"]
        if self.cleaned_data.get("last_name"): # Si añadiste last_name
            user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save() # Guarda el usuario en la base de datos
        return user
    
    
    
class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        # Excluimos 'usuario' porque se asignará automáticamente en la vista.
        # Excluimos 'fecha_creacion_proyecto' porque es auto_now_add.
        fields = ['nombre', 'descripcion', 'tiempo_estimado_general', 'fecha_inicio', 'fecha_fin_estimada', 'estado']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}), # Añadido
            'descripcion': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}), # Añadido class
            'tiempo_estimado_general': forms.TextInput(attrs={'class': 'form-control'}), # Añadido
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), # Añadido class
            'fecha_fin_estimada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), # Añadido class
            'estado': forms.Select(attrs={'class': 'form-select'}), # Para <select>, Bootstrap usa form-select
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