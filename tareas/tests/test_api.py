from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from tareas.models import Tarea, Proyecto
import json

class TareaAPITest(TestCase):
    """
    Tests para la API de Tareas (TareaViewSet)

    ¿Que vamos a probar?
    1. Autenticacion por token
    2. CRUD completo via API
    3. Permisos (solo ver datos propios)
    4. Filtros y busqueda
    5. Paginación
    """

    def setUp(self):
        """
        Preparamos datos para tests de API
        MUY IMPORTANTE: APIs usan APIClient y Token, no Client y login
        """
        # Crear usuarios
        self.user1 = User.objects.create_user(
            username='apiuser1',
            email='api1@test.com',
            password='apipass123'
        )

        self.user2 = User.objects.create_user(
            username='apiuser2',
            email='api2@test.com',
            password='api2pass123'
        )

        # Crear tokens de autenticacion
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)

        # Cliente especial para APIs
        self.client = APIClient()

        # Crear tareas de prueba
        self.tarea1 = Tarea.objects.create(
            usuario=self.user1,
            titulo='Tarea API User 1',
            completada=False
        )

        self.tarea2 = Tarea.objects.create(
            usuario=self.user2,
            titulo='Tarea API User 2',
            completada=True
        )

    
    def test_api_requiere_autenticacion(self):
        """
        Test FUNDAMENTAL: API debe rechazar requests sin token

        ¿por que es importante?
        - Seguridad: Sin token = Sin Acceso
        - APIs publicas sin auth son vulnerables
        """
        url = '/api/tareas/'

        # Requests sin token
        response = self.client.get(url)

        # Debe rechazar con 401 Unathorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_api_con_token_funciona(self):
        """
        Test: Con token válido debe funcionar
        """

        url = '/api/tareas/'
        # Token cliente
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        # PISTA: usa self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)

        response = self.client.get(url)

        # Verificar status 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar que response es JSON válido
        self.assertTrue(json.loads(response.content))

    
    def test_api_crear_tarea_post(self):
        """
        Test: POST debe crear una nueva tarea via API

        ¿Que probamos?
        - Request con JSON data
        - Status 201 CREATED
        - Tarea se crea en BD
        - Response contiene datos correctos
        - Tarea se asigna al usuario correcto
        """
        # Configurar Autenticacion
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)

        url = '/api/tareas/'
        data = {
            'titulo': 'Nueva tarea desde API',
            'descripcion': 'Creada via POST request',
            'completada': False
        }
        # Contar tareas antes
        tareas_antes = Tarea.objects.filter(usuario=self.user1).count()

        # Hacer post con JSON{
        response = self.client.post(url, data, format='json')

        # Verificar status 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar que se creo en BD
        tareas_despues = Tarea.objects.filter(usuario=self.user1).count()
        self.assertEqual(tareas_despues, tareas_antes + 1)

        # Verificar datos de respuesta
        response_data = response.json()
        self.assertEqual(response_data['titulo'], 'Nueva tarea desde API')
        self.assertEqual(response_data['descripcion'], 'Creada via POST request')
        self.assertEqual(response_data['completada'], False)

        # Verificar que se asigno al usuario correcto
        nueva_tarea = Tarea.objects.get(titulo='Nueva tarea desde API')
        self.assertEqual(nueva_tarea.usuario, self.user1)


    def test_api_solo_muestra_tareas_propias(self):
        """
        Test CRITICO: Usuario debe ver solo SUS Tareas.

        ¿Por que es importante?
        - Seguridad: Sin esto, users ven datos ajenos
        - Privacy: Datos personales protegidos
        - Compliance: Regulaciones de privacidad 
        """
        # Login como user 1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)

        url = '/api/tareas/'
        response = self.client.get(url)

        # Debe funcionar
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        # Debe tener exactamente 1 tarea ( la user1 )
        self.assertEqual(data['count'], 1)

        # Debe ser la tarea correcta
        tarea_resultado = data['results'][0]
        self.assertEqual(tarea_resultado['titulo'], 'Tarea API User 1')
        self.assertEqual(tarea_resultado['completada'], False)

        # NO debe contener tareas de user2
        titulos = [t['titulo'] for t in data['results']]
        self.assertNotIn('Tarea API User 2', titulos)


    def test_api_eliminar_tarea_delete(self):
        """
        Test: DELETE debe eliminar tarea via API
        """
       
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        # Obtener ID de la tarea a eliminar
        tarea_a_eliminar = self.tarea1.id
        url = f'/api/tareas/{tarea_a_eliminar}/'
        # Hacer DELETE
        response = self.client.delete(url)
        # Verificar status 204 NO CONTENT
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verificar que se eliminó de BD
        self.assertFalse(Tarea.objects.filter(id=tarea_a_eliminar).exists())


    def test_api_filtro_completada_true(self):
        """
        Test: Filtro ?completada=true debe mostrar solo tareas completadas
        
        ¿Por qué es importante?
        - UX: Users quieren filtrar sus datos
        - Performance: Menos datos = más rápido
        - Funcionalidad: Característica clave de tu API
        """
        # Autenticacion
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)

        # Crear tarea completada adicional
        Tarea.objects.create(
            usuario=self.user1,
            titulo='Tarea Completada',
            completada=True
        )

        # Ahora user1 tiene: 1 pendiente y 1 completada, total 2

        # Filtrar solo completadas
        url = '/api/tareas/?completada=true'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        # Debe mostrar solo 1 tarea (completada)
        self.assertEqual(data['count'], 1)

        # Verificar que es la correcta
        tarea_resultado = data['results'][0]
        self.assertEqual(tarea_resultado['titulo'], 'Tarea Completada')
        self.assertTrue(tarea_resultado['completada'])


    def test_api_filtro_completada_false(self):
        """
        Test: Filtro ?completada=false debe mostrar solo tareas pendientes
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)

        # Filtrar solo para pendientes
        url = '/api/tareas/?completada=false'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        # Verificar que todas son pendientes
        for tarea in data['results']:
            self.assertFalse(tarea['completada'])


    def test_api_busqueda_por_titulo(self):
        """
        Test: Búsqueda ?search=palabra debe encontrar tareas por título
        
        ¿Cómo funciona tu API?
        Según tu código: search_fields = ['titulo', 'descripcion']
        Busca en título Y descripción
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)

        # Crear tareas con titulos especificos
        Tarea.objects.create(
            usuario=self.user1,
            titulo='Estudiar Django testing',
            descripcion='Aprender conceptos avanzados'
        )

        Tarea.objects.create(
            usuario=self.user1,
            titulo='Comprar frutas',
            descripcion='No reacionado con testing'
        )

        # Buscar por 'testing'
        url = '/api/tareas/?search=frutas'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        # Debe encontrar un resultado (busca en titulo y descripcion)
        self.assertEqual(data['count'], 1)

        # Verificar que encontro la correcta
        tarea_encontrada = data['results'][0]
        self.assertIn('testing', tarea_encontrada['titulo'].lower() + ' ' + tarea_encontrada['descripcion'].lower())


    def test_api_paginacion_funciona(self):
        """
        Test: Paginación debe limitar resultados según configuración
        
        Tu configuración: PAGE_SIZE = 5
        Si hay más de 5 tareas, debe paginar
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)

        # Crear 7 tareas adicionales (+ 1 existente = 8 total)
        for i in range(7):
            Tarea.objects.create(
                usuario=self.user1,
                titulo=f'Tarea paginacion {i}',
                descripcion=f'Descripcion {i}'
            )

        # Primera pagina 
        url = '/api/tareas/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        # Debe mostra maximo 5 resultados
        self.assertEqual(len(data['results']), 5)

        # Debe indicar que hay mas paginas
        self.assertIsNotNone(data['next'])

        # Total debe ser 8
        self.assertEqual(data['count'], 8)


    def test_api_actualizar_parcial_patch(self):
        """
        Test: PATCH debe actualizar solo campos especificados
        """

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)

        url = f'/api/tareas/{self.tarea1.id}/'
        data = {
            'completada': True
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        # Verificar que solo cambió completada
        self.assertTrue(data['completada'])
        self.assertEqual(data['titulo'], 'Tarea API User 1')

        
    def test_api_tarea_no_existe_404(self):
        """
        Test: GET a tarea inexistente debe dar 404
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        url = '/api/tareas/99999/'  # ID que no existe
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)