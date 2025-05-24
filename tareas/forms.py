from django import forms # Importamos el módulo de formularios de Django
from .models import Tarea, Proyecto # Importamos nuestro modelo Tarea y Proyecto
from django.contrib.auth.forms import UserCreationForm # Importamos el UserCreationForm base
from django.contrib.auth.models import User # Importamos el modelo User

# Creamos una clase TareaForm que hereda de forms.ModelForm
# ModelForm es una clase especial que crea un formulario a partir de un modelo de Django.
class TareaForm(forms.ModelForm):
    # La clase 'Meta' dentro de un ModelForm le dice a Django
    # sobre qué modelo debe basarse el formulario y qué campos incluir.
    class Meta:
        # Especificamos el modelo del cual se creará el formulario.
        model = Tarea

        # 'fields' es una lista de los nombres de los campos del modelo Tarea
        # que queremos incluir en nuestro formulario.
        # No incluimos 'fecha_creacion' porque se establece automáticamente (auto_now_add=True).
        # 'completada' podría tener un valor por defecto (False), pero es bueno permitir marcarla al crear.
        fields = ['titulo', 'descripcion', 'tiempo_estimado', 'fecha_asignada', 'completada']

        # 'widgets' nos permite personalizar cómo se muestra cada campo en el HTML.
        # Por ejemplo, para 'fecha_asignada', queremos usar el input de tipo 'date' de HTML5
        # para que aparezca un selector de fecha en el navegador.
        # Para 'tiempo_estimado', podemos dejar que Django use su widget por defecto por ahora,
        # o podríamos intentar personalizarlo si el que viene por defecto no es muy usable.
        # Para 'descripcion', podemos usar un Textarea.
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}), # Añadido
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Añade una descripción detallada...', 'class': 'form-control'}), # Añadido class
            'fecha_asignada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), # Añadido class
            'tiempo_estimado': forms.TextInput(attrs={'placeholder': 'Ej: 1h30m o 0:45:00', 'class': 'form-control'}), # Añadido class
            'completada': forms.CheckboxInput(attrs={'class': 'form-check-input'}), # Para checkboxes
        }

        # 'labels' nos permite personalizar las etiquetas que se muestran junto a cada campo.
        labels = {
            'titulo': 'Título de la Tarea',
            'descripcion': 'Descripción Detallada',
            'tiempo_estimado': 'Tiempo Estimado (ej: 2h, 45m)',
            'fecha_asignada': 'Fecha Asignada',
            'completada': '¿Está Completada?',
        }

        # 'help_texts' nos permite añadir textos de ayuda adicionales para cada campo.
        help_texts = {
            'tiempo_estimado': 'Usa un formato como "1h 30m", "2 horas", "45 minutos". Django intentará interpretarlo.',
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