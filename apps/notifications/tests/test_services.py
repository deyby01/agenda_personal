"""
Tests para NotificationService.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from apps.notifications.models import Notification
from apps.notifications.services import NotificationService
from apps.tasks.models import Tarea
from apps.projects.models import Proyecto
from datetime import date, timedelta


class NotificationServiceTest(TestCase):
    """Tests para NotificationService"""
    
    def setUp(self):
        """Setup ejecutado antes de cada test"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.tarea = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Test'
        )
        
        self.proyecto = Proyecto.objects.create(
            usuario=self.user,
            nombre='Proyecto Test'
        )
    
    def test_create_task_notification(self):
        """Test: Crear notificación de tarea"""
        notification = NotificationService.create_task_notification(
            user=self.user,
            tarea=self.tarea,
            titulo='Tarea Creada',
            mensaje='Se ha creado una nueva tarea',
            subtipo='info'
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.usuario, self.user)
        self.assertEqual(notification.tarea_relacionada, self.tarea)
        self.assertEqual(notification.tipo, 'task')
        self.assertEqual(notification.subtipo, 'info')
        self.assertEqual(notification.titulo, 'Tarea Creada')
    
    def test_create_project_notification(self):
        """Test: Crear notificación de proyecto"""
        notification = NotificationService.create_project_notification(
            user=self.user,
            proyecto=self.proyecto,
            titulo='Proyecto Iniciado',
            mensaje='El proyecto ha comenzado',
            subtipo='success'
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.usuario, self.user)
        self.assertEqual(notification.proyecto_relacionado, self.proyecto)
        self.assertEqual(notification.tipo, 'project')
        self.assertEqual(notification.subtipo, 'success')
    
    def test_create_overdue_task_notification(self):
        """Test: Crear notificación de tarea atrasada"""
        # Crear tarea atrasada
        tarea_atrasada = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Atrasada',
            fecha_asignada=date.today() - timedelta(days=3),
            completada=False
        )
        
        notification = NotificationService.create_overdue_task_notification(
            tarea=tarea_atrasada
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.usuario, self.user)
        self.assertEqual(notification.tarea_relacionada, tarea_atrasada)
        self.assertEqual(notification.tipo, 'task')
        self.assertEqual(notification.subtipo, 'warning')
        self.assertIn('Atrasada', notification.titulo)
        
        # Verificar business_context
        self.assertIsNotNone(notification.business_context)
        self.assertIn('dias_atrasada', notification.business_context)
        self.assertEqual(notification.business_context['dias_atrasada'], 3)
    
    def test_create_achievement_notification(self):
        """Test: Crear notificación de logro"""
        context = {
            'achievement': '10_tasks_completed',
            'count': 10
        }
        
        notification = NotificationService.create_achievement_notification(
            user=self.user,
            titulo='¡Logro Desbloqueado!',
            mensaje='Has completado 10 tareas',
            context=context
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.usuario, self.user)
        self.assertEqual(notification.tipo, 'achievement')
        self.assertEqual(notification.subtipo, 'success')
        self.assertEqual(notification.business_context, context)
        
        # Verificar que tiene fecha de vencimiento (7 días)
        self.assertIsNotNone(notification.fecha_vencimiento)
