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

# Definimos una función llamada 'lista_tareas' que toma un objeto 'request' como argumento.
# El objeto 'request' contiene información sobre la solicitud web actual (quién la hizo, qué datos envió, etc.).
@login_required  # Decorador que asegura que solo los usuarios autenticados puedan acceder a esta vista.
def lista_tareas(request):
    # Filtramos las tareas para mostrar solo las del usuario actual
    tareas = Tarea.objects.filter(usuario=request.user).order_by('fecha_asignada', 'titulo')

    # Creamos un 'contexto'. Un contexto es un diccionario de Python donde las claves
    # son los nombres que usaremos en la plantilla, y los valores son los datos
    # que queremos pasar a la plantilla.
    # Aquí, la plantilla podrá acceder a la lista de tareas usando la variable 'lista_de_tareas_template'.
    contexto = {
        'lista_de_tareas_template': tareas
    }

    # Usamos la función render() para generar la respuesta HTTP.
    # Argumentos de render():
    # 1. request: El objeto de solicitud original.
    # 2. 'tareas/lista_tareas.html': La ruta a la plantilla HTML que queremos usar.
    #    Django buscará esta plantilla en las carpetas de plantillas configuradas.
    # 3. contexto: El diccionario con los datos que la plantilla usará.
    return render(request, 'tareas/lista_tareas.html', contexto)



@login_required  # Aseguramos que solo los usuarios autenticados puedan acceder a esta vista.
def crear_tarea(request):
    # Verificamos si el método de la solicitud es POST.
    # Esto sucede cuando el usuario envía (submits) el formulario.
    if request.method == 'POST':
        # Creamos una instancia del formulario y la llenamos con los datos de la solicitud (request.POST).
        # request.POST contiene todos los datos enviados por el formulario.
        form = TareaForm(request.POST)

        # Verificamos si el formulario es válido según las reglas definidas
        # (ej. campos obligatorios, tipos de datos correctos).
        if form.is_valid():
            # Antes de guardar, asignamos el usuario actual a la tarea
            tarea = form.save(commit=False) # No guardamos en BD todavía
            tarea.usuario = request.user    # Asignamos el usuario
            tarea.save()                    # Ahora sí guardamos

            # Después de guardar, redirigimos al usuario a la página de la lista de tareas.
            # 'lista_de_tareas_url' es el nombre que le dimos a la URL de la lista de tareas en urls.py.
            # redirect() busca una URL con ese nombre y envía al navegador del usuario allí.
            return redirect('lista_de_tareas_url')
    else:
        # Si el método no es POST (es decir, es GET, lo que significa que el usuario
        # acaba de navegar a la URL para crear una tarea),
        # creamos una instancia vacía del formulario.
        form = TareaForm()

    # Preparamos el contexto para la plantilla.
    # Pasamos el formulario (ya sea vacío o con errores si no fue válido) a la plantilla.
    contexto = {
        'formulario': form,
        'accion': 'Crear',
        'tipo_objeto': 'Tarea' # Para usar en la plantilla del formulario
    }
    # Renderizamos la plantilla 'tareas/crear_tarea.html' con el contexto.
    return render(request, 'tareas/formulario_generico.html', contexto)


@login_required  # Aseguramos que solo los usuarios autenticados puedan acceder a esta vista.
def editar_tarea(request, tarea_id): # 'tarea_id' vendrá de la URL
    # Nos aseguramos de que el usuario solo pueda editar SUS PROPIAS tareas
    tarea_obj = get_object_or_404(Tarea, id=tarea_id, usuario=request.user)

    if request.method == 'POST':
        # Creamos una instancia del formulario y la llenamos con los datos de la solicitud (request.POST)
        # Y MUY IMPORTANTE: le pasamos la 'instance=tarea_obj'.
        # Esto le dice a Django que estamos editando una instancia existente, no creando una nueva.
        form = TareaForm(request.POST, instance=tarea_obj)
        if form.is_valid():
            form.save() # Guarda los cambios en la tarea existente
            return redirect('lista_de_tareas_url')
    else:
        # Si es una solicitud GET, creamos una instancia del formulario
        # y la poblamos con los datos de la tarea existente ('instance=tarea_obj').
        # Así, el formulario aparecerá con los datos actuales de la tarea listos para editar.
        form = TareaForm(instance=tarea_obj)

    contexto = {
        'formulario': form,
        'accion': 'Editar', # Variable para el título/botón
        'tarea': tarea_obj, # Opcional: pasar el objeto tarea por si lo necesitas en la plantilla
        'tipo_objeto': 'Tarea'
    }
    # Reutilizaremos la plantilla del formulario, o crearemos una nueva si es necesario.
    # Por ahora, asumamos que vamos a generalizar la plantilla 'crear_tarea.html'.
    return render(request, 'tareas/formulario_generico.html', contexto)


@login_required
def eliminar_tarea(request, tarea_id): # 'tarea_id' vendrá de la URL
    # Nos aseguramos de que el usuario solo pueda eliminar SUS PROPIAS tareas
    tarea_obj = get_object_or_404(Tarea, id=tarea_id, usuario=request.user)

    # Si la solicitud es POST, significa que el usuario ha confirmado la eliminación.
    if request.method == 'POST':
        tarea_obj.delete() # Eliminamos el objeto Tarea de la base de datos.
        return redirect('lista_de_tareas_url') # Redirigimos a la lista de tareas.

    # Si la solicitud no es POST (es GET), mostramos la página de confirmación.
    contexto = {
        'tarea': tarea_obj,
        'url_lista_retorno': 'lista_de_tareas_url', # Para el botón "Cancelar"
    }
    return render(request, 'tareas/confirmar_eliminacion_generica.html', contexto)



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
            proyecto.save()                    # Ahora guardar en BD
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
        proyecto_obj.delete() # Eliminamos el objeto Proyecto de la base de datos.
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