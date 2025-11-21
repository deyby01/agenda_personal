"""
Tests para TareaRepository.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from apps.tasks.models import Tarea
from apps.projects.models import Proyecto
from apps.tasks.repositories import TareaRepository
from apps.core.utils import WeekRange
from datetime import date, timedelta


class TareaRepositoryTest(TestCase):
    """Tests para TareaRepository"""
    
    def setUp(self):
        """Setup ejecutado antes de cada test"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.proyecto = Proyecto.objects.create(
            usuario=self.user,
            nombre='Proyecto Test'
        )
        
        # Crear tareas de prueba
        today = date.today()
        
        self.tarea_completada = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Completada',
            completada=True,
            fecha_asignada=today
        )
        
        self.tarea_pendiente = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Pendiente',
            completada=False,
            fecha_asignada=today
        )
        
        self.tarea_atrasada = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Atrasada',
            completada=False,
            fecha_asignada=today - timedelta(days=2)
        )
    
    def test_get_tasks_for_user(self):
        """Test: Obtener todas las tareas del usuario"""
        tareas = TareaRepository.get_tasks_for_user(self.user)
        
        self.assertEqual(tareas.count(), 3)
        self.assertIn(self.tarea_completada, tareas)
        self.assertIn(self.tarea_pendiente, tareas)
        self.assertIn(self.tarea_atrasada, tareas)
    
    def test_get_tasks_for_user_in_week(self):
        """Test: Obtener tareas en un rango de semana"""
        today = date.today()
        week_range = WeekRange(
            start_date=today - timedelta(days=3),
            end_date=today + timedelta(days=3)
        )
        
        tareas = TareaRepository.get_tasks_for_user_in_week(self.user, week_range)
        
        # Debe incluir tarea_completada, tarea_pendiente, tarea_atrasada
        self.assertEqual(tareas.count(), 3)
    
    def test_get_tasks_grouped_by_date(self):
        """Test: Agrupar tareas por fecha"""
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        week_range = WeekRange(start_date=monday, end_date=sunday)
        
        grouped = TareaRepository.get_tasks_grouped_by_date(self.user, week_range)
        
        # Debe retornar dict con 7 días
        self.assertEqual(len(grouped), 7)
        
        # Verificar que hoy tiene tareas
        if today in grouped:
            tareas_hoy = grouped[today]
            self.assertGreater(len(tareas_hoy), 0)
    
    def test_get_completed_tasks_count(self):
        """Test: Contar tareas completadas"""
        count = TareaRepository.get_completed_tasks_count(self.user)
        self.assertEqual(count, 1)
    
    def test_get_total_tasks_count(self):
        """Test: Contar total de tareas"""
        count = TareaRepository.get_total_tasks_count(self.user)
        self.assertEqual(count, 3)
    
    def test_get_pending_tasks_for_user(self):
        """Test: Obtener tareas pendientes"""
        tareas = TareaRepository.get_pending_tasks_for_user(self.user)
        
        self.assertEqual(tareas.count(), 2)
        self.assertIn(self.tarea_pendiente, tareas)
        self.assertIn(self.tarea_atrasada, tareas)
        self.assertNotIn(self.tarea_completada, tareas)
    
    def test_get_overdue_tasks_for_user(self):
        """Test: Obtener tareas atrasadas"""
        tareas = TareaRepository.get_overdue_tasks_for_user(self.user)
        
        self.assertEqual(tareas.count(), 1)
        self.assertIn(self.tarea_atrasada, tareas)
        self.assertNotIn(self.tarea_pendiente, tareas)
