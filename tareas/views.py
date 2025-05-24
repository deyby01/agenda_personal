from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy # Para redirigir después de un registro exitoso
from django.views import generic # Para vistas basadas en clases genéricas
from .models import Tarea, Proyecto
from .forms import TareaForm, CustomUserCreationForm, ProyectoForm # Importamos nuestro formulario de tareas

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