"""
Task Views - View layer para Tasks domain.

Migrado desde tareas/views.py con mejoras:
- Imports actualizados a nueva arquitectura
- Uso de Repositories y Services
- Mejor separación de responsabilidades
- Docstrings comprehensivos
"""

from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import (
    CreateView, DetailView, ListView, 
    UpdateView, DeleteView, TemplateView
)
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
import datetime

from apps.tasks.models import Tarea
from apps.tasks.forms import TareaForm, TareaEstadoForm
from apps.tasks.repositories import TareaRepository
from apps.tasks.services import WeekCalculatorService, WeekNavigationService
from apps.projects.repositories import ProyectoRepository


class ListViewTasks(LoginRequiredMixin, ListView):
    """
    Vista para listar todas las tareas del usuario.
    
    Features:
    - Filtra solo tareas del usuario autenticado
    - Ordenado por fecha_asignada
    - Paginación
    - Search functionality
    
    Template: tasks/list.html
    Context: tareas (QuerySet de Tarea)
    """
    model = Tarea
    template_name = 'tareas/lista_tareas.html'
    context_object_name = 'tareas'
    paginate_by = 20
    
    def get_queryset(self):
        """
        Obtiene tareas del usuario con filtros opcionales.
        
        Returns:
            QuerySet[Tarea]: Tareas filtradas y ordenadas
        """
        # Usar repository para obtener tareas
        queryset = TareaRepository.get_tasks_for_user(self.request.user)
        
        # Filtrar por búsqueda si existe
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(titulo__icontains=search) | 
                Q(descripcion__icontains=search)
            )
        
        # Filtrar por estado si existe
        estado = self.request.GET.get('estado')
        if estado == 'completadas':
            queryset = queryset.filter(completada=True)
        elif estado == 'pendientes':
            queryset = queryset.filter(completada=False)
        
        return queryset.order_by('-fecha_asignada', '-fecha_creacion')


class CreateViewTask(LoginRequiredMixin, CreateView):
    """
    Vista para crear nuevas tareas.
    
    Features:
    - Auto-asigna usuario autenticado
    - Filtra proyectos por usuario
    - Pre-rellena fecha si viene de mi_semana
    - Success message
    
    Template: tareas/formulario_generico.html
    Success URL: lista_de_tareas_url
    """
    model = Tarea
    form_class = TareaForm
    template_name = 'tareas/formulario_generico.html'
    success_url = reverse_lazy('lista_de_tareas_url')
    
    def get_form_kwargs(self):
        """
        Añade user al form para filtrar proyectos.
        
        Returns:
            dict: Form kwargs con user
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_initial(self):
        """
        Pre-rellena fecha_asignada si viene de URL.
        
        Returns:
            dict: Initial form data
        """
        initial = super().get_initial()
        
        # Si viene fecha en query params (desde mi_semana)
        fecha = self.request.GET.get('fecha')
        if fecha:
            try:
                initial['fecha_asignada'] = datetime.datetime.strptime(
                    fecha, '%Y-%m-%d'
                ).date()
            except ValueError:
                pass
        
        return initial
    
    def form_valid(self, form):
        """
        Procesa form válido.
        
        Args:
            form: TareaForm válido
            
        Returns:
            HttpResponse: Redirect a success_url
        """
        # Asignar usuario autenticado
        form.instance.usuario = self.request.user
        
        # Guardar
        response = super().form_valid(form)
        
        # Success message
        messages.success(
            self.request,
            f'Tarea "{self.object.titulo}" creada exitosamente.'
        )
        
        return response


class DetailViewTask(LoginRequiredMixin, DetailView):
    """
    Vista de detalle de una tarea.
    
    Features:
    - Solo muestra tareas del usuario
    - Información completa de la tarea
    - Links de edición y eliminación
    
    Template: tareas/detalle_tarea.html
    Context: tarea (Tarea instance)
    """
    model = Tarea
    template_name = 'tareas/detalle_tarea.html'
    context_object_name = 'tarea'
    
    def get_queryset(self):
        """
        Filtra solo tareas del usuario.
        
        Returns:
            QuerySet[Tarea]: Tareas del usuario con proyecto relacionado
        """
        return TareaRepository.get_tasks_for_user(self.request.user)


class UpdateViewTask(LoginRequiredMixin, UpdateView):
    """
    Vista para editar tareas existentes.
    
    Features:
    - Solo permite editar propias tareas
    - Filtra proyectos por usuario
    - Success message
    - Redirect a detalle
    
    Template: tareas/formulario_generico.html
    """
    model = Tarea
    form_class = TareaForm
    template_name = 'tareas/formulario_generico.html'
    
    def get_queryset(self):
        """Filtra solo tareas del usuario."""
        return TareaRepository.get_tasks_for_user(self.request.user)
    
    def get_form_kwargs(self):
        """Añade user al form."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        """Redirect a detalle de la tarea editada."""
        return reverse('detalle_tarea_url', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """Procesa form válido con success message."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Tarea "{self.object.titulo}" actualizada exitosamente.'
        )
        return response


class DeleteViewTask(LoginRequiredMixin, DeleteView):
    """
    Vista para eliminar tareas.
    
    Features:
    - Solo permite eliminar propias tareas
    - Confirmation template
    - Success message
    - Redirect a lista
    
    Template: tareas/confirmar_eliminacion_generica.html
    Success URL: lista_de_tareas_url
    """
    model = Tarea
    template_name = 'tareas/confirmar_eliminacion_generica.html'
    success_url = reverse_lazy('lista_de_tareas_url')
    context_object_name = 'tarea'
    
    def get_queryset(self):
        """Filtra solo tareas del usuario."""
        return TareaRepository.get_tasks_for_user(self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """
        Elimina tarea con success message.
        
        Returns:
            HttpResponse: Redirect a success_url
        """
        tarea = self.get_object()
        titulo = tarea.titulo
        
        response = super().delete(request, *args, **kwargs)
        
        messages.success(
            request,
            f'Tarea "{titulo}" eliminada exitosamente.'
        )
        
        return response


class ToggleTaskStatusView(LoginRequiredMixin, View):
    """
    Vista para cambiar rápidamente el estado de completada.
    
    Ajax-friendly view que toggle el estado sin form completo.
    
    Methods:
        POST: Toggle completada status
        
    Returns:
        HttpResponse: Redirect a HTTP_REFERER o lista
    """
    
    def post(self, request, pk):
        """
        Toggle estado de completada.
        
        Args:
            request: HttpRequest
            pk: ID de la tarea
            
        Returns:
            HttpResponse: Redirect con success message
        """
        # Obtener tarea del usuario
        tarea = get_object_or_404(
            Tarea,
            pk=pk,
            usuario=request.user
        )
        
        # Toggle estado
        tarea.completada = not tarea.completada
        tarea.save()
        
        # Success message
        estado = "completada" if tarea.completada else "marcada como pendiente"
        messages.success(
            request,
            f'Tarea "{tarea.titulo}" {estado}.'
        )
        
        # Redirect a página anterior o lista
        return redirect(
            request.META.get('HTTP_REFERER', 'lista_de_tareas_url')
        )


class MyWeekView(LoginRequiredMixin, TemplateView):
    """
    Vista principal: Mi Semana.
    
    Muestra tareas organizadas por día de la semana actual.
    
    Features:
    - Navegación entre semanas
    - Tareas agrupadas por día
    - Proyectos activos
    - Week range calculation con Service Layer
    
    Template: tareas/mi_semana.html
    
    Context:
        tareas_por_dia: Dict[date, List[Tarea]]
        week_range: WeekRange
        proyectos_activos: QuerySet[Proyecto]
        nav_urls: Dict[str, str] (prev_url, next_url)
    """
    template_name = 'tareas/mi_semana.html'
    
    def get_context_data(self, **kwargs):
        """
        Prepara contexto con tareas de la semana.
        
        Returns:
            dict: Context con tareas agrupadas y navegación
        """
        context = super().get_context_data(**kwargs)
        
        # Obtener parámetros de semana
        year_param = self.kwargs.get('year')
        week_param = self.kwargs.get('week')
        
        # Parsear parámetros
        year, week = WeekCalculatorService.parse_date_params(
            year_param, week_param
        )
        
        # Calcular rango de semana
        week_range = WeekCalculatorService.get_week_range(year, week)
        
        # Obtener tareas agrupadas por día usando Repository
        tareas_por_dia = TareaRepository.get_tasks_grouped_by_date(
            self.request.user,
            week_range
        )
        
        # Obtener proyectos activos usando Repository
        proyectos_activos = ProyectoRepository.get_active_projects_for_user(
            self.request.user
        )
        
        # Generar URLs de navegación usando Service
        nav_urls = WeekNavigationService.get_navigation_urls(
            week_range,
            url_name='mi_semana_url'
        )
        
        # Actualizar contexto
        context.update({
            'tareas_por_dia': tareas_por_dia,
            'week_range': week_range,
            'proyectos_activos': proyectos_activos,
            'nav_urls': nav_urls,
            'today': timezone.localdate(),
        })
        
        return context
