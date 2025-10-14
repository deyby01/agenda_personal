from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy 
from django.views import generic, View 
from .models import Tarea, Proyecto
from .forms import TareaForm, CustomUserCreationForm, ProyectoForm
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
from .services import WeekCalculatorService, WeekNavigationService
from .repositories import TareaRepository, ProyectoRepository



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
