"""
Project Views - View layer para Projects domain.

Migrado desde tareas/views.py con mejoras:
- Imports actualizados a nueva arquitectura
- Uso de Repositories
- Mejor separación de responsabilidades
- Docstrings comprehensivos
"""

from django.shortcuts import redirect, get_list_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView, DetailView, ListView,
    UpdateView, DeleteView, TemplateView
)
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from apps.projects.models import Proyecto
from apps.projects.forms import ProyectoForm
from apps.projects.repositories import ProyectoRepository

class ListViewProjects(LoginRequiredMixin, ListView):
    """
    Vista para listar todos los proyectos del usuario.
    
    Features:
    - Filtra solo proyectos del usuario autenticado
    - Ordenado por fecha_fin_estimada
    - Paginación
    - Filtro por estado
    - Búsqueda por nombre
    
    Template: projects/list.html
    Context: lista_de_proyectos_template (QuerySet de Proyecto)
    """

    model = Proyecto
    template_name = 'projects/list.html'
    context_object_name = 'lista_de_proyectos_template'
    paginate_by = 20

    def get_queryset(self):
        """
        Obtiene proyectos del usuario con filtros opcionales.

        Returns:
            QuerySet[Proyecto]: Proyectos filtrados y ordenados.
        """
        # Obtener proyectos base del usuario
        queryset = ProyectoRepository.get_all_projects_for_user(
            user=self.request.user
        )
        
        # Filtrar por búsqueda de nombre si existe
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | 
                Q(descripcion__icontains=search)
            )
        
        # Filtrar por estado si existe
        estado = self.request.GET.get('estado', '')
        if estado and estado in dict(Proyecto.ESTADO_CHOICES):
            queryset = queryset.filter(estado=estado)
        
        return queryset.order_by('fecha_fin_estimada', 'nombre')

    def get_context_data(self, **kwargs):
        """
        Agrega información de filtros al contexto.
        
        Returns:
            dict: Context con filtros aplicados y opciones de estado
        """
        context = super().get_context_data(**kwargs)
        
        # Obtener valores actuales de filtros
        current_search = self.request.GET.get('q', '')
        current_estado = self.request.GET.get('estado', '')
        
        # Agregar al contexto
        context['current_search'] = current_search
        context['current_estado'] = current_estado
        context['estado_choices'] = Proyecto.ESTADO_CHOICES
        context['has_filters'] = bool(current_search or current_estado)
        
        return context

    

class CreateViewProject(LoginRequiredMixin, CreateView):
    """
    Vista para crear nuevos proyectos.
    
    Features:
    - Auto-asigna usuario autenticado
    - Success message
    - Context personalizado para template genérico
    
    Template: projects/form.html
    Success URL: lista_de_proyectos_url
    """
    model = Proyecto
    template_name = 'projects/form.html'
    form_class = ProyectoForm
    success_url = reverse_lazy('lista_de_proyectos_url')

    def form_valid(self, form):
        """
        Procesa form válido.
        
        Asigna usuario autenticado y añade success message.
        
        Args:
            form: ProyectoForm válido
            
        Returns:
            HttpResponse: Redirect a success_url
        """
        proyecto = form.save(commit=False)
        proyecto.usuario = self.request.user
        proyecto.save()

        messages.success(self.request, f'¡Proyecto "{proyecto.nombre}" creado exitosamente!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Prepara contexto para template genérico.
        
        Returns:
            dict: Context con etiquetas y formulario
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'accion': 'Crear',
            'tipo_objeto': 'Proyecto',
            'formulario': context['form']
        })
        return context


class DetailViewProject(LoginRequiredMixin, DetailView):
    """
    Vista de detalle de un proyecto.
    
    Features:
    - Solo muestra proyectos del usuario
    - Información completa del proyecto
    - Links de edición y eliminación
    
    Template: projects/detail.html
    Context: proyecto (Proyecto instance)
    """
    model = Proyecto
    template_name = 'projects/detail.html'
    context_object_name = 'proyecto'

    def get_queryset(self):
        """
        Filtra solo proyectos del usuario.
        
        Returns:
            QuerySet[Proyecto]: Proyectos del usuario
        """
        return ProyectoRepository.get_all_projects_for_user(self.request.user)


class UpdateViewProject(LoginRequiredMixin, UpdateView):
    """
    Vista para editar proyectos existentes.
    
    Features:
    - Solo permite editar propios proyectos
    - Success message
    - Context personalizado para template genérico
    
    Template: projects/form.html
    Success URL: lista_de_proyectos_url
    """
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'projects/form.html'
    success_url = reverse_lazy('lista_de_proyectos_url')

    def get_queryset(self):
        """ Filtra solo proyectos del usuario. """
        return ProyectoRepository.get_all_projects_for_user(self.request.user)

    def form_valid(self, form):
        """
        Procesa form válido con success message.
        """
        response = super().form_valid(form)
        messages.success(self.request, f'¡Proyecto "{form.instance.nombre}" actualizado exitosamente!')
        return response

    def get_context_data(self, **kwargs):
        """
        Prepara contexto para template genérico.
        
        Returns:
            dict: Context con etiquetas y formulario
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'accion': 'Editar',
            'tipo_objeto': 'Proyecto',
            'formulario': context['form']
        })
        return context


class DeleteViewProject(LoginRequiredMixin, DeleteView):
    """
    Vista para eliminar proyectos.
    
    Features:
    - Solo permite eliminar propios proyectos
    - Confirmation template
    - Success message
    
    Template: projects/confirm_delete.html
    Success URL: lista_de_proyectos_url
    """
    model = Proyecto
    template_name = 'projects/confirm_delete.html'
    success_url = reverse_lazy('lista_de_proyectos_url')
    context_object_name = 'objeto'

    def get_queryset(self):
        """ Filtra solo proyectos del usuario. """
        return ProyectoRepository.get_all_projects_for_user(self.request.user)

    def delete(self, request, *args, **kwargs):
        """
        Elimina proyecto con success message.
        
        Returns:
            HttpResponse: Redirect a success_url
        """
        proyecto = self.get_object()
        nombre = proyecto.nombre

        response = super().delete(request, *args, **kwargs)

        messages.success(request, f'¡Proyecto "{nombre}" eliminado exitosamente!')
        return response
    
    def get_context_data(self, **kwargs):
        """
        Prepara contexto para template de confirmación.
        
        Returns:
            dict: Context con URLs y tipo de objeto
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'url_lista_retorno': 'lista_de_proyectos_url',
            'tipo_objeto': 'Proyecto'
        })
        return context