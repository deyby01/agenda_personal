"""
Tests para ProyectoRepository.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from apps.projects.models import Proyecto
from apps.projects.repositories import ProyectoRepository
from datetime import date, timedelta


class ProyectoRepositoryTest(TestCase):
    """Tests para ProyectoRepository"""
    
    def setUp(self):
        """Setup ejecutado antes de cada test"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear varios proyectos con diferentes estados
        self.proyecto_activo = Proyecto.objects.create(
            usuario=self.user,
            nombre='Proyecto Activo',
            estado='en_curso'
        )
        
        self.proyecto_completado = Proyecto.objects.create(
            usuario=self.user,
            nombre='Proyecto Completado',
            estado='completado'
        )
        
        self.proyecto_cancelado = Proyecto.objects.create(
            usuario=self.user,
            nombre='Proyecto Cancelado',
            estado='cancelado'
        )
    
    def test_get_active_projects_for_user(self):
        """Test: Obtener solo proyectos activos"""
        proyectos = ProyectoRepository.get_active_projects_for_user(self.user)
        
        self.assertEqual(proyectos.count(), 1)
        self.assertEqual(proyectos.first(), self.proyecto_activo)

    
    def test_get_project_with_tasks_stats(self):
         """Test: Obtener proyecto con estadísticas"""
         stats = ProyectoRepository.get_project_with_tasks_stats(
             self.proyecto_activo.id,
             self.user
         )
        
         self.assertIsNotNone(stats)
         self.assertEqual(stats['proyecto'], self.proyecto_activo)
         self.assertEqual(stats['total_tareas'], 0)
         self.assertEqual(stats['completion_percentage'], 0.0)
    
    def test_get_project_with_tasks_stats_not_found(self):
        """Test: Proyecto no encontrado devuelve None"""
        stats = ProyectoRepository.get_project_with_tasks_stats(
            999999,  # ID inexistente
            self.user
        )
        
        self.assertIsNone(stats)
    
    def test_get_all_projects_for_user(self):
        """Test: Obtener todos los proyectos del usuario"""
        proyectos = ProyectoRepository.get_all_projects_for_user(self.user)
        
        self.assertEqual(proyectos.count(), 3)
    
    def test_get_completed_projects_count(self):
        """Test: Contar proyectos completados"""
        count = ProyectoRepository.get_completed_projects_count(self.user)
        
        self.assertEqual(count, 1)
    
    def test_get_active_projects_for_user_in_period(self):
        """Test: Proyectos en un período específico"""
        today = date.today()
        next_week = today + timedelta(days=7)
        
        # Proyecto con fechas en el período
        proyecto_en_periodo = Proyecto.objects.create(
            usuario=self.user,
            nombre='Proyecto en Período',
            estado='en_curso',
            fecha_inicio=today,
            fecha_fin_estimada=next_week
        )
        
        proyectos = ProyectoRepository.get_active_projects_for_user_in_period(
            self.user,
            today,
            next_week
        )
        
        self.assertIn(proyecto_en_periodo, proyectos)


    def test_get_project_with_tasks_stats_with_real_tasks(self):
        """Test: Estadísticas de proyecto con tareas reales"""
        from apps.tasks.models import Tarea
        
        # Crear tareas para el proyecto
        Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Completada',
            proyecto=self.proyecto_activo,
            completada=True
        )
        Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Pendiente',
            proyecto=self.proyecto_activo,
            completada=False
        )
        
        stats = ProyectoRepository.get_project_with_tasks_stats(
            self.proyecto_activo.id,
            self.user
        )
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats['total_tareas'], 2)
        self.assertEqual(stats['tareas_completadas'], 1)
        self.assertEqual(stats['tareas_pendientes'], 1)
        self.assertEqual(stats['completion_percentage'], 50.0)
