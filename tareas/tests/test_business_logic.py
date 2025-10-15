"""
Tests for business logic layer
"""
import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from tareas.models import Tarea, Proyecto
from tareas.business_logic import (
    TaskPrioritizationEngine, ProjectProgressCalculator,
    PriorityLevel, TaskUrgency, TaskPriorityScore
)


class TaskPrioritizationEngineTest(TestCase):
    """Test intelligent task prioritization"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Proyecto importante
        self.important_project = Proyecto.objects.create(
            nombre='Proyecto Crítico',
            descripcion='Proyecto importante',
            estado='en_curso',
            fecha_fin_estimada=timezone.localdate() + datetime.timedelta(days=15),
            usuario=self.user
        )
        
        # Tareas de test con diferentes características
        today = timezone.localdate()
        
        # Tarea vencida
        self.overdue_task = Tarea.objects.create(
            titulo='Tarea Vencida',
            fecha_asignada=today - datetime.timedelta(days=2),
            usuario=self.user
        )
        
        # Tarea que vence hoy
        self.due_today_task = Tarea.objects.create(
            titulo='Tarea Hoy',
            fecha_asignada=today,
            usuario=self.user,
            proyecto=self.important_project
        )
        
        # Tarea normal
        self.normal_task = Tarea.objects.create(
            titulo='Tarea Normal',
            fecha_asignada=today + datetime.timedelta(days=5),
            usuario=self.user
        )
        
        # Tarea sin fecha
        self.no_deadline_task = Tarea.objects.create(
            titulo='Sin Fecha',
            usuario=self.user
        )
    
    def test_overdue_task_gets_critical_priority(self):
        """Tareas vencidas deben tener prioridad crítica"""
        score = TaskPrioritizationEngine.calculate_priority_score(self.overdue_task)
        
        self.assertEqual(score.priority_level, PriorityLevel.CRITICAL)
        self.assertEqual(score.urgency_level, TaskUrgency.OVERDUE)
        self.assertTrue(score.is_critical)
        self.assertTrue(score.needs_attention)
        self.assertIn("Vencida hace", score.reasons[0])
    
    def test_due_today_task_gets_high_priority(self):
        """Tareas que vencen hoy deben tener alta prioridad"""
        score = TaskPrioritizationEngine.calculate_priority_score(self.due_today_task)
        
        self.assertEqual(score.priority_level, PriorityLevel.CRITICAL)  # 8.0 + 2.0 bonus = 10.0
        self.assertEqual(score.urgency_level, TaskUrgency.DUE_TODAY)
        self.assertTrue(score.needs_attention)
        self.assertIn("Vence hoy", score.reasons[0])
        self.assertIn("Proyecto importante", score.reasons[1])
    
    def test_normal_task_gets_medium_priority(self):
        """Tareas normales deben tener prioridad media"""
        score = TaskPrioritizationEngine.calculate_priority_score(self.normal_task)
        
        self.assertEqual(score.priority_level, PriorityLevel.MEDIUM)
        self.assertEqual(score.urgency_level, TaskUrgency.DUE_THIS_WEEK)
        self.assertFalse(score.is_critical)
    
    def test_no_deadline_task_gets_low_priority(self):
        """Tareas sin fecha deben tener prioridad baja"""
        score = TaskPrioritizationEngine.calculate_priority_score(self.no_deadline_task)
        
        self.assertEqual(score.priority_level, PriorityLevel.LOW)
        self.assertEqual(score.urgency_level, TaskUrgency.NO_DEADLINE)
        self.assertFalse(score.needs_attention)
    
    def test_prioritize_tasks_returns_sorted_list(self):
        """prioritize_tasks debe devolver lista ordenada por prioridad"""
        tasks = [self.normal_task, self.overdue_task, self.no_deadline_task, self.due_today_task]
        
        prioritized = TaskPrioritizationEngine.prioritize_tasks(tasks)
        
        # Debe estar ordenado por score (mayor a menor)
        scores = [p.score for p in prioritized]
        self.assertEqual(scores, sorted(scores, reverse=True))
        
        # Primera tarea debe ser la más crítica
        self.assertTrue(prioritized[0].score >= 10.0)  # due_today + important_project bonus
        
        # Última tarea debe ser la de menor prioridad
        self.assertTrue(prioritized[-1].score <= 3.0)  # no_deadline task


class ProjectProgressCalculatorTest(TestCase):
    """Test advanced project progress calculations"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        self.project = Proyecto.objects.create(
            nombre='Proyecto Test',
            descripcion='Proyecto para testing',
            estado='en_curso',
            fecha_fin_estimada=timezone.localdate() + datetime.timedelta(days=30),
            usuario=self.user
        )
        
        # Crear tareas: 3 completadas, 2 pendientes
        for i in range(3):
            Tarea.objects.create(
                titulo=f'Tarea Completada {i}',
                proyecto=self.project,
                usuario=self.user,
                completada=True
            )
        
        for i in range(2):
            Tarea.objects.create(
                titulo=f'Tarea Pendiente {i}',
                proyecto=self.project,
                usuario=self.user,
                completada=False
            )
    
    def test_calculate_advanced_progress_basic_metrics(self):
        """calculate_advanced_progress debe calcular métricas básicas correctamente"""
        progress = ProjectProgressCalculator.calculate_advanced_progress(self.project)
        
        # Verificar métricas básicas
        self.assertEqual(progress['total_tasks'], 5)
        self.assertEqual(progress['completed_tasks'], 3)
        self.assertEqual(progress['pending_tasks'], 2)
        self.assertEqual(progress['completion_percentage'], 60.0)  # 3/5 * 100
    
    def test_calculate_advanced_progress_includes_all_metrics(self):
        """calculate_advanced_progress debe incluir todas las métricas esperadas"""
        progress = ProjectProgressCalculator.calculate_advanced_progress(self.project)
        
        required_keys = [
            'completion_percentage', 'velocity', 'estimated_completion',
            'health_status', 'critical_tasks', 'total_tasks',
            'completed_tasks', 'pending_tasks'
        ]
        
        for key in required_keys:
            self.assertIn(key, progress)
    
    def test_project_health_assessment(self):
        """Verificar que el assessment de salud funciona correctamente"""
        # Proyecto con 60% completion debe ser 'fair'
        progress = ProjectProgressCalculator.calculate_advanced_progress(self.project)
        self.assertEqual(progress['health_status'], 'fair')
