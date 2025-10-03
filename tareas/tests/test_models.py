from django.test import TestCase
from django.contrib.auth.models import User
from tareas.models import Tarea, Proyecto
from django.utils import timezone
import datetime

class TareaModelTest(TestCase):
    """
    Test para el modelo Tarea - probamos que funciona correctamente.
    """

    def setUp(self):
        """
        setUp se ejecuta ANTES de cada test.
        Aqui creamos datos que necesitamos para las pruebas.
        """
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
    
    def test_crear_tarea_basica(self):
        """
        Test: Verificar que podemos crear una tarea basica

        PATRON AAA:
        - Arrange (Preparar): Datos necesarios.
        - Act (Actuar): Crear la tarea.
        - Assert (Verificar): Comprobar que esta bien.
        """
        # Arrange - ya tenemos self.user en el setUp()

        # Act - Crear la tarea.
        tarea = Tarea.objects.create(
            usuario=self.user,
            titulo='Primer Tarea Test'
        )

        # Assert - Verificar que se creo correctamente
        self.assertEqual(tarea.titulo, 'Primer Tarea Test')
        self.assertEqual(tarea.usuario, self.user)
        self.assertFalse(tarea.completada) # Debe ser false por defecto.
        self.assertIsNotNone(tarea.fecha_creacion) # Debe tener fecha.
    

    def test_tarea_str_method(self):
        """
        Test: Verificar que el metodo __str__ funciona.
        """

        tarea2 = Tarea.objects.create(
            usuario=self.user,
            titulo='Segunda Tarea'
        )

        self.assertEqual(str(tarea2), 'Segunda Tarea')
        self.assertEqual(tarea2.usuario, self.user)

    def test_tarea_con_todos_los_campos(self):
        """
        Test: Verificar que podemos crear tareas con todos los campos opcionales
        """
        
        # Datos para todos los campos 
        fecha_manana = timezone.now().date() + datetime.timedelta(days=1)
        tiempo_estimado = datetime.timedelta(hours=2, minutes=30)

        tarea = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Completa',
            descripcion='Una descripcion detallada',
            fecha_asignada=fecha_manana,
            tiempo_estimado=tiempo_estimado,
            completada=True
        )

        # Verificar TODOS los campos
        self.assertEqual(tarea.titulo, 'Tarea Completa')
        self.assertEqual(tarea.descripcion, 'Una descripcion detallada')
        self.assertEqual(tarea.fecha_asignada, fecha_manana)
        self.assertEqual(tarea.tiempo_estimado, tiempo_estimado)
        self.assertTrue(tarea.completada)
        self.assertEqual(tarea.usuario, self.user)

    
    def test_tarea_ordering(self):
        """
        Test: Verificar que el ordering del modelo funciona correctamente 
        El modelo tiene: ordering = ['usuario', 'fecha_asignada', 'titulo'] 
        """
        # Crear fechas diferentes
        hoy = timezone.now().date()
        manana = hoy + datetime.timedelta(days=1)

        # Crear tareas en orden incorrecto a proposito
        tarea3 = Tarea.objects.create(
            usuario=self.user,
            titulo='Z ultima tarea',
            fecha_asignada=manana
        )

        tarea1 = Tarea.objects.create(
            usuario=self.user,
            titulo='A primera tarea',
            fecha_asignada=hoy
        )

        tarea2 = Tarea.objects.create(
            usuario=self.user,
            titulo='B segunda tarea',
            fecha_asignada=hoy
        )

        # Obtener tareas ordenadas segun modelo
        tareas_ordenadas = list(Tarea.objects.filter(usuario=self.user))

        # Verificar orden correcto: fecha primero, luego titulo
        self.assertEqual(tareas_ordenadas[0], tarea1)
        self.assertEqual(tareas_ordenadas[1], tarea2)   
        self.assertEqual(tareas_ordenadas[2], tarea3)
        

    def test_tarea_usuario_requerido(self):
        """
        Test: Verificar que no se puede crear tarea sin usuario
        Este test DEBE fallar si tratamos de crear tarea sin usuario
        """
        with self.assertRaises(ValueError):
            # Esto deberia fallar.
            Tarea.objects.create(
                titulo='Tarea sin usuario'
            )



class ProyectoModelTest(TestCase):
    """
    Tests para el modelo Proyecto
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
    
    def test_crear_proyecto_basico(self):
        """
        Test: Crear proyecto con datos mínimos
        """
        
        proyecto = Proyecto.objects.create(
            nombre='Primer Proyecto',
            usuario=self.user
        )

        self.assertEqual(proyecto.nombre, 'Primer Proyecto')
        self.assertEqual(proyecto.estado, 'planificado')
        self.assertEqual(proyecto.usuario, self.user)
    
    
    def test_proyecto_str_method(self):
        """
        Test: Verificar método __str__ del proyecto
        """

        proyecto = Proyecto.objects.create(
            nombre='Nombre str',
            usuario=self.user
        )
        
        self.assertEqual(str(proyecto), 'Nombre str')
        self.assertEqual(proyecto.usuario, self.user)
