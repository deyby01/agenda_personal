"""
Tests para el modelo Proyecto.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from apps.projects.models import Proyecto
from datetime import date, timedelta

class ProyectoModelTest(TestCase):
    """ Test para el modelo Proyecto. """

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )

        self.proyecto = Proyecto.objects.create(
            usuario=self.user,
            nombre='Test Proyecto',
            descripcion='Descripción del proyecto de prueba',
            estado='planificado',
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=30),
            tiempo_estimado_general='40 horas'
        )

    def test_project_creation(self):
        """ Create simple proyect. """
        self.assertEqual(self.proyecto.nombre, 'Test Proyecto')
        self.assertEqual(self.proyecto.usuario, self.user)
        self.assertEqual(self.proyecto.estado, 'planificado')
        self.assertIsNotNone(self.proyecto.fecha_creacion)

    def test_project_str_representation(self):
        """ Test string representation of Proyecto. """
        expected = f"{self.proyecto.nombre} (Planificado)"
        self.assertEqual(str(self.proyecto), expected)
    
    def test_project_inherits_from_userownermodel(self):
        """Test: Hereda de UserOwnedModel"""
        # Debe tener campos de UserOwnedModel
        self.assertTrue(hasattr(self.proyecto, 'fecha_creacion'))
        self.assertTrue(hasattr(self.proyecto, 'fecha_modificacion'))
        self.assertTrue(hasattr(self.proyecto, 'usuario'))
        self.assertTrue(hasattr(self.proyecto, 'is_owned_by'))
    
    def test_project_is_owned_by_method(self):
        """Test: is_owned_by() helper method"""
        self.assertTrue(self.proyecto.is_owned_by(self.user))
        
        other_user = User.objects.create_user(
            username='otheruser',
            password='pass123'
        )
        self.assertFalse(self.proyecto.is_owned_by(other_user))
    
    def test_project_is_active_property(self):
        """Test: is_active property"""
        # Planificado es activo
        self.proyecto.estado = 'planificado'
        self.proyecto.save()
        self.assertTrue(self.proyecto.is_active)
        
        # En curso es activo
        self.proyecto.estado = 'en_curso'
        self.proyecto.save()
        self.assertTrue(self.proyecto.is_active)
        
        # Completado NO es activo
        self.proyecto.estado = 'completado'
        self.proyecto.save()
        self.assertFalse(self.proyecto.is_active)
        
        # Cancelado NO es activo
        self.proyecto.estado = 'cancelado'
        self.proyecto.save()
        self.assertFalse(self.proyecto.is_active)

    
    def test_project_without_tasks(self):
        """Test: Proyecto sin tareas tiene 0% completado"""
        self.assertEqual(self.proyecto.get_completion_percentage(), 0.0)
        self.assertEqual(self.proyecto.total_tareas, 0)
        self.assertEqual(self.proyecto.tareas_completadas, 0)
        self.assertEqual(self.proyecto.tareas_pendientes, 0)
    
    def test_project_state_choices(self):
        """Test: Estados válidos del proyecto"""
        estados_validos = [
            'planificado',
            'en_curso',
            'completado',
            'en_espera',
            'cancelado'
        ]
        
        for estado in estados_validos:
            self.proyecto.estado = estado
            self.proyecto.save()
            self.assertEqual(self.proyecto.estado, estado)
    
    def test_project_fields_can_be_null(self):
        """Test: Campos opcionales pueden ser null"""
        proyecto_minimal = Proyecto.objects.create(
            usuario=self.user,
            nombre='Proyecto Mínimo'
        )
        
        self.assertIsNone(proyecto_minimal.descripcion)
        self.assertIsNone(proyecto_minimal.fecha_inicio)
        self.assertIsNone(proyecto_minimal.fecha_fin_estimada)
        self.assertIsNone(proyecto_minimal.tiempo_estimado_general)
    
    def test_project_with_tasks_completion(self):
        """Test: Porcentaje de completación con tareas reales"""
        from apps.tasks.models import Tarea
        
        # Crear 4 tareas para el proyecto
        Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea 1',
            proyecto=self.proyecto,
            completada=True
        )
        Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea 2',
            proyecto=self.proyecto,
            completada=True
        )
        Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea 3',
            proyecto=self.proyecto,
            completada=False
        )
        Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea 4',
            proyecto=self.proyecto,
            completada=False
        )
        
        # Verificar counts
        self.assertEqual(self.proyecto.total_tareas, 4)
        self.assertEqual(self.proyecto.tareas_completadas, 2)
        self.assertEqual(self.proyecto.tareas_pendientes, 2)
        
        # Verificar porcentaje: 2/4 = 50%
        self.assertEqual(self.proyecto.get_completion_percentage(), 50.0)
