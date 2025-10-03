from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
from tareas.models import Tarea

class TareaViewsTest(TestCase):
    """
    Test para las vista CBV de Tarea
    """

    def setUp(self):
        """
        Preparar datos para tests de vistas
        """
        # Crear usuario 
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpassword'
        )

        # Crear otro usuario para tests de permisos
        self.otro_user = User.objects.create_user(
            username='otrouser',
            email='otro@test.com',
            password='otropassword'
        )

        # Cliente http (navegador falso)
        self.client = Client()

        # Crear tarea de prueba
        self.tarea = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea test'
        )

    def test_crear_tarea_sin_login(self):
        """
        Test: CreateViewTask debe requerir login
        Si no estas logeado -> redirect a login
        """
        url = reverse('crear_tarea_url')

        # Hacer request sin Login
        response = self.client.get(url)

        # Debe redirigir (302)
        self.assertEqual(response.status_code, 302)

        # Debe redirigir a login
        self.assertIn('/accounts/login/', response.url)


    def test_crear_tarea_con_login_muestra_formulario(self):
        """
        Test: Usuario logueado debe ver formulario.
        """
        # login del usuario
        self.client.login(username='testuser', password='testpassword')

        url = reverse('crear_tarea_url')
        response = self.client.get(url)

        # Debe cargar correctamente (200)
        self.assertEqual(response.status_code, 200)

        # Debe contener elementos del formulario
        self.assertContains(response, 'form')
        self.assertContains(response, 'titulo')

        # Verificar contexto ( datos que llegan al template )
        self.assertIn('formulario', response.context)
        self.assertEqual(response.context['accion'], 'Crear')

    
    def test_crear_tarea_post_exitoso(self):
        """
        Test: POST con datos validos debe crear la tarea 
        """
        self.client.login(username='testuser', password='testpassword')

        url = reverse('crear_tarea_url')
        data = {
            'titulo': 'Nueva tarea desde test',
            'descripcion': 'Descripcion de test',
            'completada': False
        }

        # Contar tareas antes
        tareas_antes = Tarea.objects.filter(usuario=self.user).count()

        # Hacer POST
        response = self.client.post(url, data)

        # Debe redirigir despues de crear (302)
        self.assertEqual(response.status_code, 302)

        # Debe haber creado una nueva tarea
        tareas_despues = Tarea.objects.filter(usuario=self.user).count()
        self.assertEqual(tareas_despues, tareas_antes + 1)

        # Verificar que la tarea se creo correctamente
        nueva_tarea = Tarea.objects.get(titulo='Nueva tarea desde test')
        self.assertEqual(nueva_tarea.usuario, self.user)
        self.assertEqual(nueva_tarea.descripcion, 'Descripcion de test')


    def test_lista_tareas_solo_muestra_tareas_propias(self):
        """
        Test: ListViewTasks debe mostrar solo tareas del usuario logueado
        """
        # TU CÓDIGO:
        # 1. Crear tarea para otro_user
        tarea = Tarea.objects.create(
            usuario=self.otro_user,
            titulo='Tarea otro user',
        )
        # 2. Login como self.user  
        self.client.login(username='testuser', password='testpassword')
        # 3. GET a 'lista_de_tareas_url'
        url = reverse('lista_de_tareas_url')
        response = self.client.get(url)
        # 4. Verificar que solo aparece tarea de self.user
        self.assertContains(response, 'Tarea test')
        # 5. Verificar que NO aparece tarea de otro_user
        self.assertNotContains(response, 'Tarea otro user')

        tareas_en_contexto = response.context['lista_de_tareas_template']
        self.assertEqual(len(tareas_en_contexto), 1)
