"""
Tests for repository layer components
"""
import datetime
from django.test import TestCase
from django.contrib.auth.models import User

from tareas.models import Tarea, Proyecto
from tareas.repositories import TareaRepository, ProyectoRepository
from tareas.services import WeekRange


class TareaRepositoryTest(TestCase):
    """Test TareaRepository data access methods"""
    
    def setUp(self):
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        # Crear otro usuario para verificar filtrado
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass'
        )
        
        # Crear proyecto
        self.project = Proyecto.objects.create(
            nombre='Proyecto Test',
            descripcion='Descripción test',
            usuario=self.user
        )
        
        # Crear semana de prueba
        self.week_range = WeekRange(
            datetime.date(2025, 10, 13),  # Lunes
            datetime.date(2025, 10, 19)   # Domingo
        )
        
        # Crear tareas de prueba
        self.task_monday = Tarea.objects.create(
            titulo='Tarea Lunes',
            descripcion='Descripción lunes',
            fecha_asignada=datetime.date(2025, 10, 13),
            usuario=self.user,
            proyecto=self.project
        )
        
        self.task_wednesday = Tarea.objects.create(
            titulo='Tarea Miércoles',
            descripcion='Descripción miércoles',
            fecha_asignada=datetime.date(2025, 10, 15),
            completada=True,
            usuario=self.user
        )
        
        # Tarea de otro usuario (no debería aparecer)
        self.task_other_user = Tarea.objects.create(
            titulo='Tarea Otro Usuario',
            fecha_asignada=datetime.date(2025, 10, 14),
            usuario=self.other_user
        )
        
        # Tarea fuera del rango (no debería aparecer en tests de semana)
        self.task_next_week = Tarea.objects.create(
            titulo='Tarea Semana Siguiente',
            fecha_asignada=datetime.date(2025, 10, 20),
            usuario=self.user
        )
    
    def test_get_tasks_for_user(self):
        """get_tasks_for_user debe devolver solo tareas del usuario específico"""
        tasks = TareaRepository.get_tasks_for_user(self.user)
        
        # Debe incluir todas las tareas del usuario (incluyendo fuera de semana)
        self.assertEqual(tasks.count(), 3)  # monday, wednesday, next_week
        
        # No debe incluir tareas de otros usuarios
        task_titles = [task.titulo for task in tasks]
        self.assertIn('Tarea Lunes', task_titles)
        self.assertIn('Tarea Miércoles', task_titles)
        self.assertIn('Tarea Semana Siguiente', task_titles)
        self.assertNotIn('Tarea Otro Usuario', task_titles)
    
    def test_get_tasks_for_user_in_week(self):
        """get_tasks_for_user_in_week debe filtrar por usuario y rango de fechas"""
        tasks = TareaRepository.get_tasks_for_user_in_week(self.user, self.week_range)
        
        # Solo tareas del usuario en la semana específica
        self.assertEqual(tasks.count(), 2)  # monday, wednesday
        
        task_titles = [task.titulo for task in tasks]
        self.assertIn('Tarea Lunes', task_titles)
        self.assertIn('Tarea Miércoles', task_titles)
        self.assertNotIn('Tarea Semana Siguiente', task_titles)
        self.assertNotIn('Tarea Otro Usuario', task_titles)
    
    def test_get_tasks_grouped_by_date(self):
        """get_tasks_grouped_by_date debe agrupar tareas por fecha"""
        tasks_by_date = TareaRepository.get_tasks_grouped_by_date(self.user, self.week_range)
        
        # Debe devolver diccionario con 7 días
        self.assertEqual(len(tasks_by_date), 7)
        
        # Lunes debe tener 1 tarea
        monday_tasks = tasks_by_date[datetime.date(2025, 10, 13)]
        self.assertEqual(len(monday_tasks), 1)
        self.assertEqual(monday_tasks[0].titulo, 'Tarea Lunes')
        
        # Miércoles debe tener 1 tarea
        wednesday_tasks = tasks_by_date[datetime.date(2025, 10, 15)]
        self.assertEqual(len(wednesday_tasks), 1)
        self.assertEqual(wednesday_tasks[0].titulo, 'Tarea Miércoles')
        
        # Días sin tareas deben tener lista vacía
        tuesday_tasks = tasks_by_date[datetime.date(2025, 10, 14)]
        self.assertEqual(len(tuesday_tasks), 0)
    
    def test_get_completed_tasks_count(self):
        """get_completed_tasks_count debe contar solo tareas completadas"""
        count = TareaRepository.get_completed_tasks_count(self.user, self.week_range)
        
        # Solo 1 tarea completada (miércoles)
        self.assertEqual(count, 1)
    
    def test_get_total_tasks_count(self):
        """get_total_tasks_count debe contar todas las tareas en el rango"""
        count = TareaRepository.get_total_tasks_count(self.user, self.week_range)
        
        # 2 tareas en total (lunes + miércoles)
        self.assertEqual(count, 2)


class ProyectoRepositoryTest(TestCase):
    """Test ProyectoRepository data access methods"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Proyecto activo
        self.active_project = Proyecto.objects.create(
            nombre='Proyecto Activo',
            descripcion='Activo',
            usuario=self.user,
            estado='en_curso'
        )
        
        # Proyecto inactivo
        self.inactive_project = Proyecto.objects.create(
            nombre='Proyecto Inactivo',
            descripcion='Inactivo',
            usuario=self.user,
            estado='en_espera'
        )
    
    def test_get_active_projects_for_user(self):
        """get_active_projects_for_user debe devolver solo proyectos activos"""
        projects = ProyectoRepository.get_active_projects_for_user(self.user)
        
        self.assertEqual(projects.count(), 1)
        self.assertEqual(projects.first().nombre, 'Proyecto Activo')
    
    def test_get_project_with_tasks_stats_existing(self):
        """get_project_with_tasks_stats debe calcular estadísticas correctamente"""
        # Crear tareas para el proyecto
        Tarea.objects.create(
            titulo='Tarea 1',
            usuario=self.user,
            proyecto=self.active_project,
            completada=True
        )
        Tarea.objects.create(
            titulo='Tarea 2',
            usuario=self.user,
            proyecto=self.active_project,
            completada=False
        )
        
        stats = ProyectoRepository.get_project_with_tasks_stats(self.user, self.active_project.id)
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats['project'], self.active_project)
        self.assertEqual(stats['total_tasks'], 2)
        self.assertEqual(stats['completed_tasks'], 1)
        self.assertEqual(stats['completion_percentage'], 50.0)
    
    def test_get_project_with_tasks_stats_nonexistent(self):
        """get_project_with_tasks_stats debe devolver None para proyecto inexistente"""
        stats = ProyectoRepository.get_project_with_tasks_stats(self.user, 99999)
        
        self.assertIsNone(stats)
