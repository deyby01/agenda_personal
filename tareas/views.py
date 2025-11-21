from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy 
from django.views import generic, View

from apps.tasks.business_logic import (
    TaskPrioritizationEngine,
    ProjectProgressCalculator,
    PriorityLevel
)
from apps.notifications.models import Notification
from apps.tasks.models import Tarea
from apps.projects.models import Proyecto
from apps.core.forms import CustomUserCreationForm
from apps.tasks.forms import TareaForm
from apps.projects.forms import ProyectoForm
import datetime
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q 
from django.contrib import messages 
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView, TemplateView
from rest_framework import viewsets
from .serializers import TareaSerializer, ProyectoSerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.tasks.services import WeekCalculatorService, WeekNavigationService
from apps.tasks.repositories import TareaRepository
from apps.projects.repositories import ProyectoRepository
from apps.notifications.services import NotificationService
from datetime import timedelta


class ListViewTasks(LoginRequiredMixin, ListView):
    model = Tarea
    template_name = 'tareas/lista_tareas.html'
    context_object_name = 'lista_de_tareas_template'
    
    # Override the method to filter tasks by the logged-in user
    def get_queryset(self):
        return Tarea.objects.filter(usuario=self.request.user).order_by('fecha_asignada', 'titulo')


class CreateViewTask(LoginRequiredMixin, CreateView):
    """ 
    Handle the creation of a new Tarea (task).
    
    This view ensures that only logged-in users can create tasks.
    It uses a custom form , TareaForm, and processes several pieces
    of custom logic, such as setting the task owner automatically,
    handling initial data from URL parameters, and adding extra
    context to the template.
    """
    model = Tarea
    template_name = 'tareas/formulario_generico.html'
    form_class = TareaForm
    success_url = reverse_lazy('lista_de_tareas_url') 

    def get_form_kwargs(self):
        """ Pass user to form for project filtering """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user # Pass user to form
        return kwargs
    
    def form_valid(self, form):
        """ 
        Assigns the current user as the task owner before saving.
        
        This method is called when the submitted form is valid. It
        intercepts the saving process to set the 'usuario' field
        to self.request.user and adds a success message before
        allowing the process to continue.
        """
        task = form.save(commit=False)
        task.usuario = self.request.user
        task.save()
        messages.success(self.request, f'¡Tarea "{task.titulo}" creada exitosamente!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """
        Adds extra context variables to the template.
        
        This is used to pass strings for the template's title and
        button text, making the form template more reusable.
        """
        context = super().get_context_data(**kwargs)
        context['accion'] = 'Crear'
        context['tipo_objeto'] = 'Tarea' 
        # add this line for the context worker the same as in the other views
        context['formulario'] = context['form']
        return context
    
    def get_initial(self):
        """ 
        Sets initial data for the form from URL parameters.
        
        Specifically, it checks for a 'fecha_asignada', parameter in
        the url (ej: ?fecha_asignada=2025-07-04) to pre-fill the 
        date field of the form.
        """
        initial_data = {}
        fecha_asignada_param = self.request.GET.get('fecha_asignada') 
        if fecha_asignada_param:
            try:
                initial_data['fecha_asignada'] = datetime.datetime.strptime(fecha_asignada_param, '%Y-%m-%d').date()
            except ValueError:
                # Ignores invalid date formats silently
                pass
        return initial_data


class DetailViewTask(LoginRequiredMixin, DetailView):
    """ 
    Displays the details of a single Tarea (task).
    
    This view is secured to ensure that users can only view the
    details of tasks that they own.
    """
    model = Tarea
    template_name = 'tareas/detalle_tarea.html'
    context_object_name = 'tarea'
    
    def get_queryset(self):
        """ 
        Ensures users can only view tasks they own.
        
        This method filters the queryset to only include tasks where the
        'usuario' field matches the currently logged-in user.
        """
        return Tarea.objects.filter(usuario=self.request.user)


class UpdateViewTask(LoginRequiredMixin, UpdateView):
    """ 
    Handles editing an existing Tarea (task).
    
    This view ensures a user can only edit their own tasks by filtering
    the queryset. It uses the same generic form template as the create
    view but provides different context to change titles and button text.
    """
    model = Tarea
    form_class = TareaForm
    template_name = 'tareas/formulario_generico.html'
    success_url = reverse_lazy('lista_de_tareas_url')

    def get_form_kwargs(self):
        """ Pass user to form for project filtering """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user # Pass user to form
        return kwargs
    
    def get_queryset(self):
        """
        Ensures users can only edit tasks they own.
        
        This method filters the base queryset to include only the tasks
        where the 'usuario' field matches the currently logged-in user.
        This is a critical security measure.
        """
        return Tarea.objects.filter(usuario=self.request.user)  
    
    def form_valid(self, form):
        """ 
        Adds a success message after the form is successfully update
        """
        messages.success(self.request, f'¡Tarea "{form.instance.titulo}" actualizada exitosamente!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """ 
        Adds extra context to the template to indicate an 'Edit' action.
        """
        context = super().get_context_data(**kwargs)
        context['accion'] = 'Editar'
        context['tipo_objeto'] = 'Tarea'
        context['formulario'] = context['form']
        return context


class DeleteViewTask(LoginRequiredMixin, DeleteView):
    """ 
    Handles the deletion of a specific Tarea (task).
    
    This view first shows a confirmation page before deleting the object.
    It is secured to ensure users can only delete their own tasks.
    It also provides extra context to the template for dynamic content,
    such as the URL for the 'Cancel' button.
    """
    model = Tarea
    template_name = 'tareas/confirmar_eliminacion_generica.html'
    success_url = reverse_lazy('lista_de_tareas_url')
    context_object_name = 'objeto' 
    
    def get_queryset(self):
        """ 
        Ensures users can only access tasks they own.
        
        This method filters the queryset to include only tasks where the
        'usuario' field matches the currently logged-in user, preventing
        unauthorized access to other users' tasks.
        """
        return super().get_queryset().filter(usuario=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """ 
        Adds a success message before deleting the object.
        
        This method is called when the user confirms the deletion via on POST
        request. It retrieves the object's title for the message and then 
        calls the parent method to perform the actual deletion.
        """
        object_title = self.get_object().titulo
        messages.success(request, f'¡Tarea "{object_title}" eliminada exitosamente!')
        return super().delete(request, *args, **kwargs)        
    
    def get_context_data(self, **kwargs):
        """ 
        Adds the specific URL name for the 'Cancel' button to the context.
        """
        context = super().get_context_data(**kwargs)
        context['url_lista_retorno'] = 'lista_de_tareas_url'
        return context


class VistaRegistro(generic.CreateView):
    form_class = CustomUserCreationForm 
    success_url = reverse_lazy('login')
    template_name = 'registration/registro.html' 
    

class ListViewProjects(LoginRequiredMixin, ListView):
    """
    Displays a list of projects owned by the current user.

    The view is restricted to authenticated users and filters the
    projects to show only those belonging to the person making the
    request. The projects are ordered by their estimated end date
    and then by name.
    """
    model = Proyecto
    template_name = 'tareas/lista_proyectos.html'
    context_object_name = 'lista_de_proyectos_template'
    
    def get_queryset(self):
        """
        Returns a queryset of projects filtered by the current user.
        """
        return Proyecto.objects.filter(usuario=self.request.user).order_by('fecha_fin_estimada', 'nombre')
    

class CreateViewProject(LoginRequiredMixin, CreateView):
    """
    Handles the creation of a new Proyecto (Project).

    This view ensures only authenticated users can create projects.
    It automatically assigns the new project to the current user
    and provides extra context to the generic form template.
    """
    model = Proyecto
    template_name = 'tareas/formulario_generico.html'
    form_class = ProyectoForm
    success_url = reverse_lazy('lista_de_proyectos_url')
    
    def form_valid(self, form):
        """
        Assigns the current user as the project owner before saving.

        This method is called after form validation. It sets the 'usuario'
        field to the current user and adds a success message before the
        final save and redirect.
        """
        project = form.save(commit=False)
        project.usuario = self.request.user
        project.save()
        messages.success(self.request, f'¡Proyecto "{project.nombre}" creado exitosamente!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """
        Adds extra context for the generic form template.

        This includes providing the correct variable name ('formulario')
        that the template expects for the form object.
        """
        context = super().get_context_data(**kwargs)
        context['accion'] = 'Crear'
        context['tipo_objeto'] = 'Proyecto'
        context['formulario'] = context['form']
        return context


class DetailViewProject(LoginRequiredMixin, DetailView):
    """
    Displays the details of a single Proyecto (Project).

    This view is secured to ensure that users can only view the
    details of projects that they own.
    """
    model = Proyecto
    template_name = 'tareas/detalle_proyecto.html'
    context_object_name = 'proyecto'
    
    def get_queryset(self):
        """
        Ensures users can only view projects they own.
        """
        return Proyecto.objects.filter(usuario=self.request.user)
  

class UpdateViewProject(LoginRequiredMixin, UpdateView):
    """
    Handles editing an existing Proyecto (Project).

    This view is secured to ensure a user can only edit their own
    projects by filtering the queryset. It uses a generic form
    template and provides extra context to customize it for an
    "Edit" action.
    """
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'tareas/formulario_generico.html'
    success_url = reverse_lazy('lista_de_proyectos_url')

    def get_queryset(self):
        """
        Ensures users can only edit projects they own.
        """
        return super().get_queryset().filter(usuario=self.request.user)
    
    def form_valid(self, form):
        """
        Adds a success message after the form is successfully updated.
        """
        messages.success(self.request, f'¡Proyecto "{form.instance.nombre}" actualizado exitosamente!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """
        Adds extra context for the generic form template.
        """
        context = super().get_context_data(**kwargs)
        context['accion'] = 'Editar'
        context['tipo_objeto'] = 'Proyecto'
        context['formulario'] = context['form']
        return context


class DeleteViewProject(LoginRequiredMixin, DeleteView):
    """
    Handles the deletion of a specific Proyecto (Project).

    This view first shows a confirmation page before deleting the
    object. It is secured to ensure users can only delete projects
    they own and provides extra context to the template for the
    'Cancel' button URL.
    """
    model = Proyecto
    template_name = 'tareas/confirmar_eliminacion_generica.html'
    success_url = reverse_lazy('lista_de_proyectos_url')
    context_object_name = 'objeto'  
    
    def get_queryset(self):
        """
        Ensures users can only access projects they own.
        """
        return super().get_queryset().filter(usuario=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """
        Adds a success message before deleting the object.
        """
        object_title = self.get_object().nombre
        messages.success(request, f'¡Proyecto "{object_title}" eliminado exitosamente!')
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """
        Adds extra context for the generic confirmation template.
        """
        context = super().get_context_data(**kwargs)
        context['url_lista_retorno'] = 'lista_de_proyectos_url' 
        context['tipo_objeto'] = 'Proyecto' 
        return context


class MyWeekView(LoginRequiredMixin, TemplateView):
    """
    SOLID-Compliant MyWeekView implementation

    Single Responsibility: ONLY handles HTTP request/response and template rendering.
    - No business logic (delegated to services)
    - No data access logic (delegated to repositories) 
    - No date calculations (delegated to services)
    
    This follows:
    - SRP: Single responsibility (HTTP handling only)
    - DIP: Depends on abstractions (services/repositories)
    - OCP: Open for extension via service composition
    """
    template_name = 'tareas/mi_semana.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        base_date = WeekCalculatorService.parse_date_params(
            kwargs.get('anio'),
            kwargs.get('mes'),
            kwargs.get('dia')
        )

        # Calculate week range (Service Responsability)
        current_week = WeekCalculatorService.get_week_range(base_date)

        # Get navigation data (Service Responsability)
        navigation_week = WeekCalculatorService.get_navigation_weeks(current_week)
        navigation_urls = WeekNavigationService.get_navigation_urls(current_week, navigation_week)
        create_task_urls = WeekNavigationService.get_create_task_urls(current_week)

        # Get user's tasks for the week (Repository Responsibility)
        tasks_by_date = TareaRepository.get_tasks_grouped_by_date(self.request.user, current_week)

        # Get active projects (Repository Responsibility)
        active_projects = ProyectoRepository.get_active_projects_for_user_in_period(
            self.request.user,
            current_week.start_date,
            current_week.end_date,
        )

        # Get week statistics (Repository Responsibility)
        completed_count = TareaRepository.get_completed_tasks_count(self.request.user, current_week)
        total_count = TareaRepository.get_total_tasks_count(self.request.user, current_week)

        # Build context (View responsibility - presentation logic only)
        context.update({
            'rango_fechas_str': current_week.format_display(),
            'es_semana_actual': current_week.is_current_week,
            'dias_con_tareas': self._transform_tasks_to_template_format(tasks_by_date, create_task_urls),
            'semana_anterior_url': navigation_urls.get('previous'),
            'semana_siguiente_url': navigation_urls.get('next'),
            'proyectos_activos': active_projects,

            'completed_count': completed_count,
            'total_count': total_count,
            'completion_percentage': self._calculate_completion_percentage(completed_count, total_count)

        })

        return context
    

    def _transform_tasks_to_template_format(self, tasks_by_date, create_task_urls):
        """
        Transforms SOLID repository data to match original template structure.
        This is pure presentation logic - stays in view.
        """

        today = timezone.localdate()

        dias_con_tareas = []

        # Iterate through week days in order
        for date in sorted(tasks_by_date.keys()):
            # Map day name for URL lookup
            day_name = date.strftime('%A').lower()

            dias_con_tareas.append({
                'fecha': date,
                'tareas': tasks_by_date[date], # Lists of taks for this day
                'es_hoy': date == today,
                'url_crear_tarea_dia': create_task_urls.get(day_name, '')
            })
        
        return dias_con_tareas
    
    def _calculate_completion_percentage(self, completed: int, total: int) -> float:
        """
        Simple helper method for presentation calculation.
        This stays in the view beacuse it's pure presentation logic,
        not business logic that would need testing.
        """
        if total == 0.0:
            return 0.0
        return round((completed / total) * 100, 1)  



class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Intelligent Dashboard View - Deyby's Vision Implementation
    
    Features:
    - Task prioritization using TaskPrioritizationEngine  
    - Priority zones: Critical, Attention, Future
    - Real-time task scoring and categorization
    
    Security: Requires authentication via LoginRequiredMixin
    """
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        """Prepare intelligent dashboard data using business logic"""
        context = super().get_context_data(**kwargs)
        
        # Get user's tasks
        user_tasks = Tarea.objects.filter(usuario=self.request.user)
        # Get user's projects
        user_projects = Proyecto.objects.filter(usuario=self.request.user)
        
        # 🚀 USE YOUR TaskPrioritizationEngine
        prioritized_task_scores = TaskPrioritizationEngine.prioritize_tasks(user_tasks)
        
        # Create efficient task lookup dictionary
        tasks_dict = {task.id: task for task in user_tasks}
        
        # Organize by priority zones
        critical_tasks = []
        attention_tasks = []
        future_tasks = []
        
        for task_score in prioritized_task_scores:
            # Get actual task object using task_id
            task = tasks_dict.get(task_score.task_id)
            if not task:
                continue
                
            # Create combined data for template  
            task_data = {
                'task': task,
                'priority_level': task_score.priority_level,
                'urgency_level': task_score.urgency_level,
                'score': task_score.score,
                'reasons': task_score.reasons
            }
            
            # Categorize into priority zones
            if task_score.priority_level == PriorityLevel.CRITICAL:
                critical_tasks.append(task_data)
            elif task_score.priority_level in [PriorityLevel.HIGH, PriorityLevel.MEDIUM]:
                attention_tasks.append(task_data)
            else:  # LOW priority
                future_tasks.append(task_data)

        # DUAL ORGANIZATION - Health status + Project state
        projects_by_health = {
            'healthy': [],
            'at_risk': [],
            'critical': [],
            'completed': []
        }

        projects_by_status = {
            'planificado': [],
            'en_curso': [],
            'completado': [],
            'en_espera': [],
            'cancelado': []
        }

        total_projects = 0

        for proyecto in user_projects:
            # Calculate ADVANCED progress for each project
            progress_data = ProjectProgressCalculator.calculate_advanced_progress(proyecto)

            # Calculate days remaining manually
            if proyecto.fecha_fin_estimada:
                today = timezone.now().date()
                days_remaining = (proyecto.fecha_fin_estimada - today).days
            else:
                days_remaining = None

            # Create comprehensive project data
            project_data = {
                'project': proyecto,
                'progress_data': progress_data,
                'percentage': progress_data['completion_percentage'],
                'velocity': progress_data['velocity'],
                'days_remaining': days_remaining,
                'health_status': progress_data['health_status'],
                'estimated_completion': progress_data['estimated_completion'],
                'total_tasks': progress_data['total_tasks'],
                'completed_tasks': progress_data['completed_tasks'],
                'pending_tasks': progress_data['pending_tasks'],
                'critical_tasks': progress_data['critical_tasks']
            }

            # ORGANIZATION 1: By Health Status 
            if proyecto.estado == 'completado':
                projects_by_health['completed'].append(project_data)
            elif progress_data['health_status'] == 'critical':
                projects_by_health['critical'].append(project_data)
            elif progress_data['health_status'] == 'at_risk':
                projects_by_health['at_risk'].append(project_data)
            else: # Healthy
                projects_by_health['healthy'].append(project_data)

            # Organize by project status
            if proyecto.estado in projects_by_status:
                projects_by_status[proyecto.estado].append(project_data)

            total_projects += 1

        # Generar notificaciones al acceder al dashboard
        NotificationService.generate_daily_notifications(self.request.user)

        today = timezone.now().date()

        # Completadas hoy (para motivacion inmediata)
        completed_today = Tarea.objects.filter(
            usuario=self.request.user,
            completada=True,
            fecha_asignada=today, # Completadas que vencian hoy
        ).order_by('-id')[:5] # Maximo 5 mas recientes

        # Estadisticas motivacionales
        completed_this_week = Tarea.objects.filter(
            usuario=self.request.user,
            completada=True,
            fecha_asignada__gte=today - timedelta(days=7)
        ).count()

        total_completed_ever = Tarea.objects.filter(
            usuario=self.request.user,
            completada=True,
        ).count()



        # Add to context
        context.update({
            'critical_tasks': critical_tasks,
            'attention_tasks': attention_tasks, 
            'future_tasks': future_tasks,
            'total_tasks': len(prioritized_task_scores),

            'projects_by_health': projects_by_health,
            'projects_by_status': projects_by_status,
            'total_projects': total_projects,

            # Quick stats with correct names
            'planificado_count': len(projects_by_status['planificado']),
            'en_curso_count': len(projects_by_status['en_curso']),
            'completado_count': len(projects_by_status['completado']),
            'en_espera_count': len(projects_by_status['en_espera']),
            'cancelado_count': len(projects_by_status['cancelado']),

            # Gamificacion - Motivacion del usuario
            'completed_tasks_today': completed_today,
            'completed_this_week': completed_this_week,
            'total_completed_ever': total_completed_ever,
        })
        
        return context


class NotificationCenterView(LoginRequiredMixin, ListView):
    """
    Centro de notificaciones

    Caracteristicas:
    - Todas las notificaciones del usuario
    - Diferenciacion visual ( leidas vs no leidas )
    - Ordenadas poro fecha ( más recientes primero )
    - Paginación para performance
    """
    model = Notification
    template_name = 'notificaciones/centro_notificaciones.html'
    context_object_name = 'notificaciones'
    paginate_by = 20

    def get_queryset(self):
        """ Solo notificaciones del usuario logeado """
        return Notification.objects.filter(
            usuario=self.request.user
        ).select_related(
            'tarea_relacionada',
            'proyecto_relacionado'
        ).order_by('-fecha_creacion')


    def get_context_data(self, **kwargs):
        """ Agregar estadisticas para la pagina """
        context = super().get_context_data(**kwargs)
        user_notifications = self.get_queryset()

        context.update({
            'total_notifications': user_notifications.count(),
            'unread_count': user_notifications.filter(leida=False).count(),
            'read_count': user_notifications.filter(leida=True).count(),
            'critical_count': user_notifications.filter(subtipo='critical').count(),
            'warning_count': user_notifications.filter(subtipo='warning').count()
        })

        return context

class NotificationClickView(LoginRequiredMixin, View):
    """
    Manejo de click en notificación

    Funcionalidad:
    - Marcar notificación como leida
    - Redirigir al origen (tarea/proyecto relacionado)
    - Actualizar contador automaticamente
    """
    def get(self, request, notification_id):
        """
        Procesar click en notificación.
        """
        # Obtener notificacion del usuario
        try:
            notification = Notification.objects.get(
                id=notification_id,
                usuario=request.user
            )
        except Notification.DoesNotExist:
            messages.error(request, 'Notificación no encontrada.')
            return redirect('centro_notificaciones')

        # Marcar como leida
        notification.leida = True
        notification.save()

        # Redirect inteligente
        if notification.tarea_relacionada:
            messages.success(request, f'Revisando tarea: {notification.tarea_relacionada.titulo}')
            return redirect('detalle_tarea_url', pk=notification.tarea_relacionada.id)
        
        elif notification.proyecto_relacionado:
            messages.success(request, f'Revisando proyecto: {notification.proyecto_relacionado.nombre}')
            return redirect('detalle_proyecto_url', pk=notification.proyecto_relacionado.id)

        else:
            # Notificación sin relación especifica
            messages.info(request, 'Notificación marcada como leida.')
            return redirect('centro_notificaciones')


class ToggleTaskStatusView(LoginRequiredMixin, View):
    """
    Handles toggling the completion status of a single task.

    This view does not render a template. It only responds to POST
    requests to perform a specific action and then redirects the
-    user, making it an efficient endpoint for quick updates.
    """
    def post(self, request, *args, **kwargs):
        """
        Inverts the 'completada' field of a specified Tarea.

        Fetches a task securely, ensuring it belongs to the logged-in
        user, toggles its boolean 'completada' status, saves the
        change, and adds a success message before redirecting.
        """
        task_id = self.kwargs.get('tarea_id')
        task = get_object_or_404(Tarea, id=task_id, usuario=self.request.user)
        
        task.completada = not task.completada
        task.save()
        
        status_str = "completada" if task.completada else "marcada como pendiente"
        messages.success(request, f'¡Tarea "{task.titulo}" {status_str} exitosamente!')
        
        redirect_url_param = self.request.GET.get('next_week_view')
        if redirect_url_param:
            return redirect(redirect_url_param)
        
        return redirect('mi_semana_actual_url')







# =========== VIEWS FOR API ===========
class TareaViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for Tarea model.

    This view is responsible for performing CRUD operations on the Tarea model.
    """
    serializer_class = TareaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['completada', 'proyecto']
    search_fields = ['titulo', 'descripcion']

    def get_queryset(self):
        """
        Returns a queryset of Tarea objects filtered by the current user.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Tarea.objects.none()
        return Tarea.objects.filter(usuario=self.request.user)
    
    def perform_create(self, serializer):
        """
        Saves a new Tarea instance with the current user as the author and handle 
        project assigment during creation.
        """
        proyecto_id = serializer.validated_data.pop('proyecto_id', None)
        tarea = serializer.save(usuario=self.request.user)

        if proyecto_id:
            try:
                proyecto = Proyecto.objects.get(id=proyecto_id, usuario=self.request.user)
                tarea.proyecto = proyecto
                tarea.save()
            except Proyecto.DoesNotExist:
                pass


class ProyectoViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for Proyecto model.

    This view is responsible for performing CRUD operations on the Proyecto model.
    """
    serializer_class = ProyectoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['estado']
    search_fields = ['nombre', 'descripcion']
    
    def get_queryset(self):
        """
        Returns a queryset of Proyecto objects filtered by the current user.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Proyecto.objects.none()
        return Proyecto.objects.filter(usuario=self.request.user)
    
    def perform_create(self, serializer):
        """
        Saves a new Proyecto instance with the current user as the author.
        """
        serializer.save(usuario=self.request.user)
