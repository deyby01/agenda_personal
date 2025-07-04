from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy # Para redirigir después de un registro exitoso
from django.views import generic # Para vistas basadas en clases genéricas
from .models import Tarea, Proyecto
from .forms import TareaForm, CustomUserCreationForm, ProyectoForm # Importamos nuestro formulario de tareas
import datetime
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q # Para consultas OR complejas
from django.contrib import messages # ¡Importamos el framework de mensajes!
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView


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
    
    def get_queryset(self):
        """
        Ensures users can only edit tasks they own.
        
        This method filters the base queryset to include only the tasks
        where the 'usuario' field matches the currently logged-in user.
        This is a critical security measure.
        """
        return super().get_queryset().filter(usuario=self.request.user)  
    
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




@login_required
def eliminar_proyecto(request, proyecto_id): # 'proyecto_id' vendrá de la URL
    # Obtenemos la instancia del Proyecto que queremos eliminar.
    # Solo el usuario propietario puede eliminarlo.
    proyecto_obj = get_object_or_404(Proyecto, id=proyecto_id, usuario=request.user)

    if request.method == 'POST':
        nombre_eliminado = proyecto_obj.nombre # Guardamos el nombre del proyecto para el mensaje
        proyecto_obj.delete() # Eliminamos el objeto Proyecto de la base de datos.
        messages.success(request, f"¡Proyecto '{nombre_eliminado}' eliminado exitosamente!")
        return redirect('lista_de_proyectos_url') # Redirigimos a la lista de proyectos.

    # Si la solicitud no es POST (es GET), mostramos la página de confirmación.
    contexto = {
        'objeto': proyecto_obj, # Usaremos 'objeto' para que la plantilla sea más genérica
        'tipo_objeto': 'Proyecto',
        'url_lista_retorno': 'lista_de_proyectos_url' # Para el botón "Cancelar"
    }
    # Reutilizaremos la plantilla de confirmación de eliminación
    return render(request, 'tareas/confirmar_eliminacion_generica.html', contexto)


@login_required
def mi_semana_view(request, anio=None, mes=None, dia=None):
    # Determinar la fecha base para la semana
    if anio and mes and dia:
        try:
            fecha_base = datetime.date(int(anio), int(mes), int(dia))
        except ValueError:
            # Si la fecha no es válida, redirigir a la semana actual
            return redirect(reverse('mi_semana_actual_url')) # Necesitaremos esta URL
    else:
        fecha_base = timezone.localdate()

    # Calcular el inicio de la semana (lunes) y el fin de la semana (domingo)
    # weekday() devuelve 0 para lunes y 6 para domingo
    inicio_semana = fecha_base - datetime.timedelta(days=fecha_base.weekday())
    fin_semana = inicio_semana + datetime.timedelta(days=6)

    # Fechas para los botones de navegación
    semana_anterior_fecha = inicio_semana - datetime.timedelta(days=7)
    semana_siguiente_fecha = inicio_semana + datetime.timedelta(days=7)

    # Determinar si es la semana actual
    hoy = timezone.localdate()
    es_semana_actual = (inicio_semana <= hoy <= fin_semana)

    # Preparar datos para la plantilla
    dias_con_tareas = []
    for i in range(7):
        fecha_dia_actual = inicio_semana + datetime.timedelta(days=i)
        tareas_del_dia = Tarea.objects.filter(
            usuario=request.user,
            fecha_asignada=fecha_dia_actual
        ).order_by('completada', 'titulo') # Ordenar por completada y luego título

        # Para el enlace "+Añadir Tarea"
        url_crear_tarea_dia = f"{reverse('crear_tarea_url')}?fecha_asignada={fecha_dia_actual.strftime('%Y-%m-%d')}"

        dias_con_tareas.append({
            'fecha': fecha_dia_actual,
            'tareas': tareas_del_dia,
            'es_hoy': fecha_dia_actual == hoy,
            'url_crear_tarea_dia': url_crear_tarea_dia
        })

    # Formatear rango de fechas para el título
    # Si el inicio y fin de semana están en el mismo mes
    if inicio_semana.month == fin_semana.month:
        rango_fechas_str = f"{inicio_semana.strftime('%d')} - {fin_semana.strftime('%d %b %Y')}"
    else: # Si abarcan meses diferentes
        rango_fechas_str = f"{inicio_semana.strftime('%d %b')} - {fin_semana.strftime('%d %b %Y')}"

    # --- NUEVA LÓGICA PARA PROYECTOS ACTIVOS EN LA SEMANA ---
    proyectos_activos = Proyecto.objects.filter(
        Q(usuario=request.user),
        # Proyectos que comienzan antes o durante esta semana Y terminan durante o después de esta semana.
        # O proyectos sin fecha de inicio pero que terminan durante o después de esta semana.
        # O proyectos sin fecha de fin pero que comienzan antes o durante esta semana.
        # O proyectos sin fechas de inicio ni fin (se muestran siempre si no están completados/cancelados)
        (
            Q(fecha_inicio__lte=fin_semana, fecha_fin_estimada__gte=inicio_semana) | # Caso principal: se solapa
            Q(fecha_inicio__lte=fin_semana, fecha_fin_estimada__isnull=True) |       # Inicia en/antes, sin fecha fin
            Q(fecha_inicio__isnull=True, fecha_fin_estimada__gte=inicio_semana) |    # Sin fecha inicio, termina en/después
            Q(fecha_inicio__isnull=True, fecha_fin_estimada__isnull=True)            # Sin fechas (mostrar siempre activos)
        ),
        ~Q(estado__in=['completado', 'cancelado']) # Excluir completados o cancelados
    ).distinct().order_by('fecha_fin_estimada', 'nombre')
    # El .distinct() es importante si un proyecto pudiera coincidir con múltiples condiciones Q y duplicarse.

    contexto = {
        'dias_con_tareas': dias_con_tareas,
        'rango_fechas_str': rango_fechas_str,
        'es_semana_actual': es_semana_actual,
        'semana_anterior_url': reverse('mi_semana_especifica_url', args=[semana_anterior_fecha.year, semana_anterior_fecha.month, semana_anterior_fecha.day]) if not es_semana_actual else None,
        'semana_siguiente_url': reverse('mi_semana_especifica_url', args=[semana_siguiente_fecha.year, semana_siguiente_fecha.month, semana_siguiente_fecha.day]),
        'proyectos_activos': proyectos_activos, # <--- NUEVO DATO PARA LA PLANTILLA
    }
    return render(request, 'tareas/mi_semana.html', contexto) 



@login_required
def cambiar_estado_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id, usuario=request.user)
    if request.method == 'POST':
        # No necesitamos un formulario completo aquí si solo cambiamos un booleano.
        # Simplemente invertimos el estado.
        tarea.completada = not tarea.completada
        tarea.save()
        estado_str = "completada" if tarea.completada else "marcada como pendiente"
        messages.success(request, f'¡Tarea "{tarea.titulo}" {estado_str} exitosamente!') # Mensaje de éxito

    # Redirigir de vuelta a la vista semanal.
    # Necesitamos saber a qué semana volver. Podríamos pasar la fecha de inicio de semana
    # como un parámetro en la URL de 'cambiar_estado_tarea' o en los datos POST.
    # Por simplicidad ahora, redirigimos a la semana actual.
    # Una mejor solución sería redirigir a la semana que se estaba viendo.

    # Para redirigir a la semana que se estaba viendo, necesitamos esa fecha.
    # Si la pasamos como parámetro GET en la URL de la acción del formulario:
    redirect_url_param = request.GET.get('next_week_view')
    if redirect_url_param:
        return redirect(redirect_url_param)

    # Fallback a la semana actual si no se especifica 'next_week_view'
    return redirect(reverse('mi_semana_actual_url'))




# NUEVA VISTA para el detalle de un proyecto
@login_required
def detalle_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id, usuario=request.user)
    # Opcional: Podríamos obtener tareas asociadas a este proyecto si tuviéramos una relación
    # tareas_del_proyecto = Tarea.objects.filter(proyecto=proyecto, usuario=request.user) 
    # Pero actualmente no hay un campo 'proyecto' en el modelo Tarea.

    contexto = {
        'proyecto': proyecto,
        # 'tareas_del_proyecto': tareas_del_proyecto, # Si las tuviéramos
    }
    return render(request, 'tareas/detalle_proyecto.html', contexto)