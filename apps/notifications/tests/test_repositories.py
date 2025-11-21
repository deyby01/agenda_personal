"""
Tests para NotificationRepository.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from apps.notifications.models import Notification
from apps.notifications.repositories import NotificationRepository
from apps.tasks.models import Tarea
from datetime import timedelta


class NotificationRepositoryTest(TestCase):
    """Tests para NotificationRepository"""
    
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
        
        # Crear notificaciones de prueba
        self.notification_unread = Notification.objects.create(
            usuario=self.user,
            titulo='Notificación No Leída',
            mensaje='Mensaje',
            tipo='task',
            subtipo='info',
            leida=False
        )
        
        self.notification_read = Notification.objects.create(
            usuario=self.user,
            titulo='Notificación Leída',
            mensaje='Mensaje',
            tipo='task',
            subtipo='info',
            leida=True
        )
        
        self.notification_critical = Notification.objects.create(
            usuario=self.user,
            titulo='Notificación Crítica',
            mensaje='Mensaje urgente',
            tipo='system',
            subtipo='critical',
            leida=False
        )
    
    def test_get_all_for_user(self):
        """Test: Obtener todas las notificaciones del usuario"""
        notifications = NotificationRepository.get_all_for_user(self.user)
        
        self.assertEqual(notifications.count(), 3)
        self.assertIn(self.notification_unread, notifications)
        self.assertIn(self.notification_read, notifications)
        self.assertIn(self.notification_critical, notifications)
    
    def test_get_unread_for_user(self):
        """Test: Obtener notificaciones no leídas"""
        notifications = NotificationRepository.get_unread_for_user(self.user)
        
        self.assertEqual(notifications.count(), 2)
        self.assertIn(self.notification_unread, notifications)
        self.assertIn(self.notification_critical, notifications)
        self.assertNotIn(self.notification_read, notifications)
    
    def test_get_unread_count(self):
        """Test: Contar notificaciones no leídas"""
        count = NotificationRepository.get_unread_count(self.user)
        self.assertEqual(count, 2)
    
    def test_get_critical_unread(self):
        """Test: Obtener notificaciones críticas no leídas"""
        notifications = NotificationRepository.get_critical_unread(self.user)
        
        self.assertEqual(notifications.count(), 1)
        self.assertIn(self.notification_critical, notifications)
    
    def test_get_by_type(self):
        """Test: Filtrar por tipo"""
        task_notifications = NotificationRepository.get_by_type(self.user, 'task')
        
        self.assertEqual(task_notifications.count(), 2)
        self.assertIn(self.notification_unread, task_notifications)
        self.assertIn(self.notification_read, task_notifications)
        
        system_notifications = NotificationRepository.get_by_type(self.user, 'system')
        self.assertEqual(system_notifications.count(), 1)
    
    def test_get_recent(self):
        """Test: Obtener notificaciones recientes"""
        # Crear notificación antigua
        old_notification = Notification.objects.create(
            usuario=self.user,
            titulo='Notificación Antigua',
            mensaje='Mensaje',
            tipo='task',
            subtipo='info'
        )
        # Forzar fecha antigua
        old_date = timezone.now() - timedelta(days=10)
        Notification.objects.filter(pk=old_notification.pk).update(
            fecha_creacion=old_date
        )
        
        # Obtener recientes (últimos 7 días)
        recent = NotificationRepository.get_recent(self.user, days=7)
        
        # Las 3 originales deberían estar, la antigua no
        self.assertEqual(recent.count(), 3)
        self.assertNotIn(old_notification, recent)
    
    def test_mark_all_as_read(self):
        """Test: Marcar todas como leídas"""
        updated = NotificationRepository.mark_all_as_read(self.user)
        
        self.assertEqual(updated, 2)  # Eran 2 sin leer
        
        # Verificar que ahora todas están leídas
        unread_count = NotificationRepository.get_unread_count(self.user)
        self.assertEqual(unread_count, 0)
    
    def test_delete_old_notifications(self):
        """Test: Eliminar notificaciones antiguas leídas"""
        # Crear notificación antigua y leída
        old_notification = Notification.objects.create(
            usuario=self.user,
            titulo='Notificación Antigua Leída',
            mensaje='Mensaje',
            tipo='task',
            subtipo='info',
            leida=True
        )
        old_date = timezone.now() - timedelta(days=35)
        Notification.objects.filter(pk=old_notification.pk).update(
            fecha_creacion=old_date
        )
        
        # Eliminar antiguas (>30 días)
        deleted = NotificationRepository.delete_old_notifications(self.user, days=30)
        
        self.assertEqual(deleted, 1)
        
        # Verificar que se eliminó
        exists = Notification.objects.filter(pk=old_notification.pk).exists()
        self.assertFalse(exists)
