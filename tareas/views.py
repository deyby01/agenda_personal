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
from django.views.generic import CreateView, ListView, UpdateView, DeleteView


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
        tarea = form.save(commit=False)
        tarea.usuario = self.request.user 
        tarea.save()
        messages.success(self.request, f'¡Tarea "{tarea.titulo}" creada exitosamente!') 
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
    # Usamos el UserCreationForm que Django provee.
    form_class = CustomUserCreationForm # Usamos nuestro formulario personalizado

    # En caso de éxito (el formulario es válido y el usuario se crea),
    # redirigimos al usuario a la URL nombrada 'login'.
    # reverse_lazy se usa aquí porque las URLs no se cargan cuando se importa el archivo,
    # por lo que necesitamos una forma "perezosa" (lazy) de obtener la URL.
    success_url = reverse_lazy('login')

    # Especificamos la plantilla HTML que se usará para mostrar el formulario de registro.
    template_name = 'registration/registro.html' # La crearemos a continuación
    
    
@login_required # Protegemos la lista de proyectos
def lista_proyectos(request):
    # Filtramos los proyectos para mostrar solo los del usuario actual
    # Ordenamos por fecha_fin_estimada y luego por nombre
    proyectos = Proyecto.objects.filter(usuario=request.user).order_by('fecha_fin_estimada', 'nombre')

    contexto = {
        'lista_de_proyectos_template': proyectos
    }
    return render(request, 'tareas/lista_proyectos.html', contexto) # Usaremos una nueva plantilla


@login_required
def crear_proyecto(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False) # No guardar en BD todavía
            proyecto.usuario = request.user    # Asignar el usuario actual
            proyecto.save()                     # Ahora guardar en BD
            messages.success(request, f'¡Proyecto "{proyecto.nombre}" creado exitosamente!') # Mensaje de éxito
            return redirect('lista_de_proyectos_url') # Redirigir a la lista de proyectos
    else:
        form = ProyectoForm()

    contexto = {
        'formulario': form,
        'tipo_objeto': 'Proyecto', # Para usar en la plantilla del formulario
        'accion': 'Crear'
    }
    # Podríamos crear una plantilla específica 'formulario_proyecto.html' o generalizar más.
    # Por ahora, vamos a crear una copia de formulario_tarea.html y la llamaremos formulario_generico.html
    return render(request, 'tareas/formulario_generico.html', contexto)


@login_required
def editar_proyecto(request, proyecto_id): # 'proyecto_id' vendrá de la URL
    # Obtenemos la instancia del Proyecto que queremos editar.
    # Solo el usuario propietario puede editarlo.
    proyecto_obj = get_object_or_404(Proyecto, id=proyecto_id, usuario=request.user)

    if request.method == 'POST':
        # Creamos una instancia del formulario con los datos de la solicitud (request.POST)
        # y la instancia del proyecto existente (instance=proyecto_obj).
        form = ProyectoForm(request.POST, instance=proyecto_obj)
        if form.is_valid():
            form.save() # Guarda los cambios en el proyecto existente
            messages.success(request, f"¡Proyecto '{proyecto_obj.nombre}' actualizado exitosamente!")
            return redirect('lista_de_proyectos_url') # Redirige a la lista de proyectos
    else:
        # Si es una solicitud GET, creamos una instancia del formulario
        # poblada con los datos del proyecto existente (instance=proyecto_obj).
        form = ProyectoForm(instance=proyecto_obj)

    contexto = {
        'formulario': form,
        'accion': 'Editar',
        'tipo_objeto': 'Proyecto',
        'objeto': proyecto_obj # Pasamos el objeto por si queremos mostrar su nombre u otra info en la plantilla
    }
    return render(request, 'tareas/formulario_generico.html', contexto)


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


# NUEVA VISTA para el detalle de una tarea
@login_required
def detalle_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id, usuario=request.user)
    contexto = {
        'tarea': tarea
    }
    return render(request, 'tareas/detalle_tarea.html', contexto)


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