"""
Tests para Bug Fixes - Regression Testing

Arquitecto de QA: Deyby Camacho
Metodología: TDD para bug fixes - test first, fix after  
Propósito: Asegurar que corrections no rompan functionality existente
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from tareas.models import Tarea
from tareas.business_logic import TaskPrioritizationEngine


class TaskPrioritizationBugFixTest(TestCase):
    """
    Tests para bug de tareas completadas en zones críticas
    
    Bug reportado: TaskPrioritizationEngine incluye tareas completadas
    Solución: Filtrar solo tareas pendientes (completada=False)
    """
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        
    def test_prioritization_engine_excludes_completed_tasks(self):
        """
        PASO 1: TaskPrioritizationEngine NO debe incluir tareas completadas
        
        Este test DEBE FALLAR inicialmente (refleja bug actual)
        Después del fix, debe pasar
        """
        # Crear tarea completada crítica (NO debe aparecer en resultados)
        completed_critical = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Completada Crítica',
            descripcion='Esta tarea está done pero era crítica',
            fecha_asignada=timezone.now().date() - timedelta(days=5),  # Super vencida
            completada=True  # ← COMPLETADA - NO debe analizarse
        )
        
        # Crear tarea pendiente crítica (SÍ debe aparecer)
        pending_critical = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Pendiente Crítica', 
            descripcion='Esta tarea es crítica y requiere acción',
            fecha_asignada=timezone.now().date() - timedelta(days=2),  # Vencida
            completada=False  # ← PENDIENTE - SÍ debe analizarse
        )
        
        # EJECUTAR ENGINE DE PRIORIZACIÓN
        user_tasks = Tarea.objects.filter(usuario=self.user)
        prioritized_results = TaskPrioritizationEngine.prioritize_tasks(user_tasks)
        
        # DEBUGGING: Ver qué tareas se analizan
        print(f"DEBUG: Total user tasks: {user_tasks.count()}")
        print(f"DEBUG: Prioritized results: {len(prioritized_results)}")
        
        for result in prioritized_results:
            task = Tarea.objects.get(id=result.task_id)
            print(f"  - Task: {task.titulo} (completada: {task.completada}) - Score: {result.score}")
        
        # VERIFICACIONES DEL BUG FIX
        
        # 1. NO debe incluir tarea completada
        completed_task_ids = [r.task_id for r in prioritized_results if Tarea.objects.get(id=r.task_id).completada]
        self.assertEqual(len(completed_task_ids), 0, 
                        "Engine NO debe incluir tareas completadas en análisis de prioridad")
        
        # 2. SÍ debe incluir tarea pendiente
        pending_task_ids = [r.task_id for r in prioritized_results if not Tarea.objects.get(id=r.task_id).completada]
        self.assertEqual(len(pending_task_ids), 1, 
                        "Engine debe incluir solo tareas pendientes")
        
        # 3. La tarea pendiente debe ser la que encontramos
        self.assertIn(pending_critical.id, pending_task_ids)
        self.assertNotIn(completed_critical.id, [r.task_id for r in prioritized_results])
        
        # 4. Verificar que el análisis de la tarea pendiente es correcto
        pending_result = next(r for r in prioritized_results if r.task_id == pending_critical.id)
        self.assertGreater(pending_result.score, 5.0, "Tarea vencida debe tener score alto")
        
    def test_current_tests_still_work_after_bug_fix(self):
        """
        PASO 2: Verificar que tests existentes siguen funcionando
        
        Regression test - existing functionality debe mantenerse
        """
        # Crear solo tareas pendientes (como tests existentes probablemente hacen)
        pending_task1 = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Pendiente 1',
            fecha_asignada=timezone.now().date(),
            completada=False  # Pendiente
        )
        
        pending_task2 = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Pendiente 2',
            fecha_asignada=timezone.now().date() - timedelta(days=1),  # Más crítica
            completada=False  # Pendiente
        )
        
        # El engine debe funcionar igual que antes con tareas pendientes
        user_tasks = Tarea.objects.filter(usuario=self.user)
        results = TaskPrioritizationEngine.prioritize_tasks(user_tasks)
        
        # Debe procesar ambas tareas pendientes
        self.assertEqual(len(results), 2)
        
        # La más vencida debe tener mayor score
        task_scores = {r.task_id: r.score for r in results}
        self.assertGreater(task_scores[pending_task2.id], task_scores[pending_task1.id])
