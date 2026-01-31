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
from datetime import timedelta

from apps.core.forms import CustomUserCreationForm
from apps.tasks.models import Tarea
from apps.tasks.forms import TareaForm, TareaEstadoForm
from apps.tasks.repositories import TareaRepository
from apps.tasks.services import WeekCalculatorService, WeekNavigationService
from apps.projects.repositories import ProyectoRepository
from apps.notifications.services import NotificationService

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
    template_name = 'tasks/list.html'
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
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(
                Q(titulo__icontains=search) |
                Q(descripcion__icontains=search)
            )

        # Filtrar por estado si existe
        estado = self.request.GET.get('estado', '')
        if estado == 'completadas':
            queryset = queryset.filter(completada=True)
        elif estado == 'pendientes':
            queryset = queryset.filter(completada=False)

        return queryset.order_by('-fecha_asignada', '-fecha_creacion')

    def get_context_data(self, **kwargs):
        """
        Agrega información de filtros al contexto y asegura compatibilidad
        con template legado que espera lista_de_tareas_template.

        Returns:
            dict: Context con filtros aplicados y lista de tareas
        """
        context = super().get_context_data(**kwargs)

        # Compatibilidad con template legado
        context['lista_de_tareas_template'] = context.get('tareas')

        # Obtener valores actuales de filtros
        current_search = self.request.GET.get('q', '')
        current_estado = self.request.GET.get('estado', '')

        # Agregar al contexto
        context['current_search'] = current_search
        context['current_estado'] = current_estado
        context['has_filters'] = bool(current_search or current_estado)

        return context


class TaskFormContextMixin:
    """
    Mixin para asegurar que el template genérico de formularios
    reciba siempre los valores esperados (accion, tipo_objeto, formulario).
    """
    action_label = 'Crear'
    object_type_label = 'Tarea'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('accion', self.action_label)
        context.setdefault('tipo_objeto', self.object_type_label)
        # Compatibilidad con template heredado que espera 'formulario'
        context['formulario'] = context.get('form')
        return context


class CreateViewTask(TaskFormContextMixin, LoginRequiredMixin, CreateView):
    """
    Vista para crear nuevas tareas.

    Features:
    - Auto-asigna usuario autenticado
    - Filtra proyectos por usuario
    - Pre-rellena fecha si viene de mi_semana
    - Success message

    Template: tasks/form.html
    Success URL: lista_de_tareas_url
    """
    model = Tarea
    form_class = TareaForm
    template_name = 'tasks/form.html'
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
        fecha = self.request.GET.get('fecha') or self.request.GET.get('fecha_asignada')
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

    Template: tasks/detail.html
    Context: tarea (Tarea instance)
    """
    model = Tarea
    template_name = 'tasks/detail.html'
    context_object_name = 'tarea'

    def get_queryset(self):
        """
        Filtra solo tareas del usuario.

        Returns:
            QuerySet[Tarea]: Tareas del usuario con proyecto relacionado
        """
        return TareaRepository.get_tasks_for_user(self.request.user)


class UpdateViewTask(TaskFormContextMixin, LoginRequiredMixin, UpdateView):
    """
    Vista para editar tareas existentes.

    Features:
    - Solo permite editar propias tareas
    - Filtra proyectos por usuario
    - Success message
    - Redirect a detalle

    Template: tasks/form.html
    """
    model = Tarea
    form_class = TareaForm
    template_name = 'tasks/form.html'

    action_label = 'Editar'

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

    Template: tasks/confirm_delete.html
    Success URL: lista_de_tareas_url
    """
    model = Tarea
    template_name = 'tasks/confirm_delete.html'
    success_url = reverse_lazy('lista_de_tareas_url')
    context_object_name = 'tarea'

    def get_queryset(self):
        """Filtra solo tareas del usuario."""
        return TareaRepository.get_tasks_for_user(self.request.user)

    def get_context_data(self, **kwargs):
        """
        Asegura compatibilidad con plantilla legacy que espera
        tipo_objeto, objeto y url_lista_retorno.
        """
        context = super().get_context_data(**kwargs)
        context.setdefault('tipo_objeto', 'Tarea')
        context.setdefault('objeto', context.get('tarea'))
        context.setdefault('url_lista_retorno', 'lista_de_tareas_url')
        return context

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

class VistaRegistro(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('account_login')
    template_name = 'registration/registro.html'

class MyWeekView(LoginRequiredMixin, TemplateView):
    """
    Vista principal: Mi Semana.

    Muestra tareas organizadas por día de la semana actual.

    Features:
    - Navegación entre semanas
    - Tareas agrupadas por día
    - Proyectos activos
    - Week range calculation con Service Layer

    Template: tasks/my_week.html

    Context:
        tareas_por_dia: Dict[date, List[Tarea]]
        week_range: WeekRange
        proyectos_activos: QuerySet[Proyecto]
        nav_urls: Dict[str, str] (prev_url, next_url)
    """
    template_name = 'tasks/my_week.html'

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
        year_parsed, week_parsed = WeekCalculatorService.parse_week_params(
            str(year_param) if year_param else None,
            str(week_param) if week_param else None
        )

        # Calcular rango de semana
        week_range = WeekCalculatorService.get_week_range_from_week_number(year_parsed, week_parsed)

        navigation_weeks = WeekCalculatorService.get_navigation_weeks(week_range)

        # Generar URLs de navegación usando Service
        nav_urls = WeekNavigationService.get_navigation_urls(
            week_range,
            navigation_weeks,
            url_name='mi_semana_url'
        )

        create_task_urls = WeekNavigationService.get_create_task_urls(week_range)

        # Obtener tareas agrupadas por día usando Repository
        tareas_por_dia = TareaRepository.get_tasks_grouped_by_date(
            self.request.user,
            week_range
        )

        # Obtener proyectos activos usando Repository
        proyectos_activos = ProyectoRepository.get_active_projects_for_user(
            self.request.user
        )

        completed_count = TareaRepository.get_completed_tasks_count(
            self.request.user,
            week_range
        )

        total_count = TareaRepository.get_total_tasks_count(
            self.request.user,
            week_range
        )

        tareas_sin_fecha = TareaRepository.get_tasks_without_date(self.request.user)

        dias_con_tareas = self._transform_tasks_to_template_format(
            tareas_por_dia,
            create_task_urls
        )

        # Actualizar contexto
        context.update({
            'tareas_por_dia': dias_con_tareas,  # legacy compatibility
            'dias_con_tareas': dias_con_tareas,
            'week_range': week_range,
            'proyectos_activos': proyectos_activos,
            'nav_urls': nav_urls,
            'today': timezone.localdate(),
            'completed_count': completed_count,
            'total_count': total_count,
            'completion_percentage': self._calculate_completion_percentage(completed_count, total_count),
            'rango_fechas_str': week_range.format_display(),
            'es_semana_actual': week_range.is_current_week,
            'semana_anterior_url': nav_urls.get('previous'),
            'semana_siguiente_url': nav_urls.get('next'),
            'tareas_sin_fecha': tareas_sin_fecha,
        })

        return context

    def _transform_tasks_to_template_format(self, tasks_by_date, create_task_urls=None):
        """
        Transforma datos del repository al formato del template.

        Args:
            tasks_by_date: Dict[date, List[Tarea]]

        Returns:
            list: Lista de díccionarios con formato para template
        """
        today = timezone.localdate()
        dias_con_tareas = []

        # Iterar through week days en orden
        for date in sorted(tasks_by_date.keys()):
            day_name = date.strftime('%A').lower()
            dias_con_tareas.append({
                'fecha': date,
                'tareas': tasks_by_date[date],
                'es_hoy': date == today,
                'url_crear_tarea_dia': (create_task_urls or {}).get(day_name, '')
            })

        return dias_con_tareas

    def _calculate_completion_percentage(self, completed: int, total: int) -> float:
        """
        Calcula porcentaje de completación.

        Args:
            completed: Tareas completadas
            total: Total de tareas

        Returns:
            float: Porcentaje (0-100)
        """
        if total == 0:
            return 0.0
        return round((completed / total) * 100, 1)


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard Inteligente - Implementación de visión de Deyby.

    Features:
    - Priorización de tareas usando TaskPrioritizationEngine
    - Zonas de prioridad: Critical, Attention, Future
    - Puntuación y categorización en tiempo real
    - Organización de proyectos por salud y estado
    - Gamificación y motivación del usuario
    - Estadísticas de completación

    Security: Requiere autenticación via LoginRequiredMixin
    """
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        """
        Prepara datos inteligentes del dashboard.

        Returns:
            dict: Context con tareas priorizadas y proyectos organizados
        """
        context = super().get_context_data(**kwargs)

        # Obtener tareas del usuario
        user_tasks = TareaRepository.get_tasks_for_user(self.request.user)

        # Obtener proyectos del usuario
        user_projects = ProyectoRepository.get_all_projects_for_user(
            self.request.user
        )

        from apps.tasks.business_logic import (
            TaskPrioritizationEngine,
            ProjectProgressCalculator,
            PriorityLevel
        )

        prioritized_task_scores = TaskPrioritizationEngine.prioritize_tasks(
            user_tasks
        )

        # Crear diccionario eficiente de tareas
        tasks_dict = {task.id: task for task in user_tasks}

        # Organizar por zonas de prioridad
        critical_tasks = []
        attention_tasks = []
        future_tasks = []

        for task_score in prioritized_task_scores:
            # Obtener objeto de tarea usando task_id
            task = tasks_dict.get(task_score.task_id)
            if not task:
                continue

            # Crear datos combinados para template
            task_data = {
                'task': task,
                'priority_level': task_score.priority_level,
                'urgency_level': task_score.urgency_level,
                'score': task_score.score,
                'reasons': task_score.reasons
            }

            # Categorizar en zonas de prioridad
            if task_score.priority_level == PriorityLevel.CRITICAL:
                critical_tasks.append(task_data)
            elif task_score.priority_level in [
                PriorityLevel.HIGH,
                PriorityLevel.MEDIUM
            ]:
                attention_tasks.append(task_data)
            else:  # LOW priority
                future_tasks.append(task_data)

        # ========== ORGANIZACIÓN DUAL - Salud + Estado ==========

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
            # Calcular progreso AVANZADO para cada proyecto
            progress_data = ProjectProgressCalculator.calculate_advanced_progress(
                proyecto
            )

            # Calcular días restantes manualmente
            if proyecto.fecha_fin_estimada:
                today = timezone.localdate()
                days_remaining = (proyecto.fecha_fin_estimada - today).days
            else:
                days_remaining = None

            # Crear datos comprehensivos del proyecto
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

            # ORGANIZACIÓN 1: Por estado de salud
            if proyecto.estado == 'completado':
                projects_by_health['completed'].append(project_data)
            elif progress_data['health_status'] == 'critical':
                projects_by_health['critical'].append(project_data)
            elif progress_data['health_status'] == 'at_risk':
                projects_by_health['at_risk'].append(project_data)
            else:  # Healthy
                projects_by_health['healthy'].append(project_data)

            # Organizar por estado del proyecto
            if proyecto.estado in projects_by_status:
                projects_by_status[proyecto.estado].append(project_data)

            total_projects += 1

        # Generar notificaciones al acceder al dashboard
        NotificationService.generate_daily_notifications(self.request.user)

        today = timezone.localdate()

        # Completadas hoy (para motivación inmediata)
        completed_today = Tarea.objects.filter(
            usuario=self.request.user,
            completada=True,
            fecha_asignada=today,
        ).order_by('-id')[:5]  # Máximo 5 más recientes

        # Estadísticas motivacionales
        completed_this_week = Tarea.objects.filter(
            usuario=self.request.user,
            completada=True,
            fecha_asignada__gte=today - timedelta(days=7)
        ).count()

        total_completed_ever = Tarea.objects.filter(
            usuario=self.request.user,
            completada=True,
        ).count()

        # Añadir al contexto
        context.update({
            'critical_tasks': critical_tasks,
            'attention_tasks': attention_tasks,
            'future_tasks': future_tasks,
            'total_tasks': len(prioritized_task_scores),

            'projects_by_health': projects_by_health,
            'projects_by_status': projects_by_status,
            'total_projects': total_projects,

            # Estadísticas rápidas con nombres correctos
            'planificado_count': len(projects_by_status['planificado']),
            'en_curso_count': len(projects_by_status['en_curso']),
            'completado_count': len(projects_by_status['completado']),
            'en_espera_count': len(projects_by_status['en_espera']),
            'cancelado_count': len(projects_by_status['cancelado']),

            # Gamificación - Motivación del usuario
            'completed_tasks_today': completed_today,
            'completed_this_week': completed_this_week,
            'total_completed_ever': total_completed_ever,
        })

        return context
