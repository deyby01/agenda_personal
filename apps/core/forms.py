"""
Core Forms - Shared forms across the application.

Forms que no pertenecen a un dominio específico:
- User authentication
- Registration
- Profile management
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML, Div
from allauth.account.forms import LoginForm


class CustomUserCreationForm(UserCreationForm):
    """
    Form personalizado para registro de usuarios.
    
    Extiende UserCreationForm con:
    - Email obligatorio
    - Validación de email único
    - Styling con crispy forms
    
    Usage:
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
    """
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """Personalizar widgets de password fields."""
        super().__init__(*args, **kwargs)
        
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    
    def clean_email(self):
        """
        Validar que el email sea único.
        
        Returns:
            str: Email validado
            
        Raises:
            ValidationError: Si el email ya existe
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Este email ya está registrado. Por favor usa otro.'
            )
        return email
    
    def save(self, commit=True):
        """
        Guardar usuario con email.
        
        Args:
            commit: Si True, guarda en BD inmediatamente
            
        Returns:
            User: Usuario creado
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomLoginForm(LoginForm):
    """
    Form personalizado para login con django-allauth.
    
    Personaliza el estilo del form de login estándar.
    
    Usage:
        # En settings.py:
        ACCOUNT_FORMS = {
            'login': 'apps.core.forms.CustomLoginForm',
        }
    """
    
    def __init__(self, *args, **kwargs):
        """Personalizar widgets."""
        super().__init__(*args, **kwargs)
        
        # Personalizar field de login (username o email)
        if 'login' in self.fields:
            self.fields['login'].widget.attrs.update({
                'class': 'form-control',
                'placeholder': 'Usuario o Email'
            })
        
        # Personalizar field de password
        if 'password' in self.fields:
            self.fields['password'].widget.attrs.update({
                'class': 'form-control',
                'placeholder': 'Contraseña'
            })
        
        # Personalizar remember field si existe
        if 'remember' in self.fields:
            self.fields['remember'].widget.attrs.update({
                'class': 'form-check-input'
            })
