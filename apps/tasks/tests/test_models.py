"""
Tests para el modelo Tarea.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from apps.tasks.models import Tarea
from apps.projects.models import Proyecto
from datetime import date, timedelta


class TareaModelTest(TestCase):
    """Tests para el modelo Tarea"""
    
    def setUp(self):
        """Setup ejecutado antes de cada test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.proyecto = Proyecto.objects.create(
            usuario=self.user,
            nombre='Proyecto Test',
            estado='en_curso'
        )
        
        self.tarea = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Test',
            descripcion='Descripción de prueba',
            completada=False,
            fecha_asignada=date.today(),
            proyecto=self.proyecto
        )
    
    def test_task_creation(self):
        """Test: Crear tarea básica"""
        self.assertEqual(self.tarea.titulo, 'Tarea Test')
        self.assertEqual(self.tarea.usuario, self.user)
        self.assertEqual(self.tarea.proyecto, self.proyecto)
        self.assertFalse(self.tarea.completada)
        self.assertIsNotNone(self.tarea.fecha_creacion)
    
    def test_task_str_representation(self):
        """Test: __str__ method"""
        # Tarea no completada
        expected = "⬜ Tarea Test"
        self.assertEqual(str(self.tarea), expected)
        
        # Tarea completada
        self.tarea.completada = True
        self.tarea.save()
        expected = "✅ Tarea Test"
        self.assertEqual(str(self.tarea), expected)
    
    def test_task_inherits_from_userownedmodel(self):
        """Test: Hereda de UserOwnedModel"""
        self.assertTrue(hasattr(self.tarea, 'fecha_creacion'))
        self.assertTrue(hasattr(self.tarea, 'fecha_modificacion'))
        self.assertTrue(hasattr(self.tarea, 'usuario'))
        self.assertTrue(hasattr(self.tarea, 'is_owned_by'))
    
    def test_task_is_owned_by_method(self):
        """Test: is_owned_by() helper method"""
        self.assertTrue(self.tarea.is_owned_by(self.user))
        
        other_user = User.objects.create_user(
            username='otheruser',
            password='pass123'
        )
        self.assertFalse(self.tarea.is_owned_by(other_user))
    
    def test_task_is_completed_property(self):
        """Test: is_completed property"""
        self.assertFalse(self.tarea.is_completed)
        
        self.tarea.completada = True
        self.tarea.save()
        self.assertTrue(self.tarea.is_completed)
    
    def test_task_is_overdue_property(self):
        """Test: is_overdue property"""
        # Tarea futura: NO atrasada
        self.tarea.fecha_asignada = date.today() + timedelta(days=1)
        self.tarea.save()
        self.assertFalse(self.tarea.is_overdue)
        
        # Tarea pasada y NO completada: SÍ atrasada
        self.tarea.fecha_asignada = date.today() - timedelta(days=1)
        self.tarea.completada = False
        self.tarea.save()
        self.assertTrue(self.tarea.is_overdue)
        
        # Tarea pasada pero COMPLETADA: NO atrasada
        self.tarea.completada = True
        self.tarea.save()
        self.assertFalse(self.tarea.is_overdue)
        
        # Tarea sin fecha: NO atrasada
        self.tarea.fecha_asignada = None
        self.tarea.completada = False
        self.tarea.save()
        self.assertFalse(self.tarea.is_overdue)
    
    def test_task_project_name_property(self):
        """Test: project_name property"""
        # Con proyecto
        self.assertEqual(self.tarea.project_name, 'Proyecto Test')
        
        # Sin proyecto
        self.tarea.proyecto = None
        self.tarea.save()
        self.assertEqual(self.tarea.project_name, 'No project')
    
    def test_task_without_project(self):
        """Test: Tarea sin proyecto es válida"""
        tarea_sin_proyecto = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Independiente',
            completada=False
        )
        
        self.assertIsNone(tarea_sin_proyecto.proyecto)
        self.assertEqual(tarea_sin_proyecto.project_name, 'No project')
    
    def test_task_project_relationship(self):
        """Test: Relación Task -> Project"""
        # Tarea tiene acceso al proyecto
        self.assertEqual(self.tarea.proyecto.nombre, 'Proyecto Test')
        
        # Proyecto tiene acceso a sus tareas
        tareas_del_proyecto = self.proyecto.tareas.all()
        self.assertIn(self.tarea, tareas_del_proyecto)
        self.assertEqual(tareas_del_proyecto.count(), 1)
    
    def test_task_fields_can_be_null(self):
        """Test: Campos opcionales pueden ser null"""
        tarea_minimal = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Mínima'
        )
        
        self.assertIsNone(tarea_minimal.descripcion)
        self.assertIsNone(tarea_minimal.tiempo_estimado)
        self.assertIsNone(tarea_minimal.fecha_asignada)
        self.assertIsNone(tarea_minimal.proyecto)
