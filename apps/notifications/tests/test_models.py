"""
Tests para el modelo Notification.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from apps.notifications.models import Notification
from apps.tasks.models import Tarea
from apps.projects.models import Proyecto
from datetime import timedelta


class NotificationModelTest(TestCase):
    """Tests para el modelo Notification"""
    
    def setUp(self):
        """Setup ejecutado antes de cada test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
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
        
        self.notification = Notification.objects.create(
            usuario=self.user,
            titulo='Notificación Test',
            mensaje='Mensaje de prueba',
            tipo='task',
            subtipo='info',
            tarea_relacionada=self.tarea
        )
    
    def test_notification_creation(self):
        """Test: Crear notificación básica"""
        self.assertEqual(self.notification.titulo, 'Notificación Test')
        self.assertEqual(self.notification.usuario, self.user)
        self.assertEqual(self.notification.tipo, 'task')
        self.assertEqual(self.notification.subtipo, 'info')
        self.assertFalse(self.notification.leida)
        self.assertFalse(self.notification.accionada)
    
    def test_notification_str_representation(self):
        """Test: __str__ method"""
        str_repr = str(self.notification)
        self.assertIn('Notificación Test', str_repr)
        self.assertIn('testuser', str_repr)
        # Debe incluir emoji
        self.assertIn('ℹ️', str_repr)
    
    def test_notification_inherits_from_userownedmodel(self):
        """Test: Hereda de UserOwnedModel"""
        self.assertTrue(hasattr(self.notification, 'fecha_creacion'))
        self.assertTrue(hasattr(self.notification, 'fecha_modificacion'))
        self.assertTrue(hasattr(self.notification, 'usuario'))
        self.assertTrue(hasattr(self.notification, 'is_owned_by'))
    
    def test_notification_urgency_icon_property(self):
        """Test: urgency_icon property"""
        # Critical
        self.notification.subtipo = 'critical'
        self.assertEqual(self.notification.urgency_icon, '🚨')
        
        # Warning
        self.notification.subtipo = 'warning'
        self.assertEqual(self.notification.urgency_icon, '⚠️')
        
        # Info
        self.notification.subtipo = 'info'
        self.assertEqual(self.notification.urgency_icon, 'ℹ️')
        
        # Success
        self.notification.subtipo = 'success'
        self.assertEqual(self.notification.urgency_icon, '✅')
    
    def test_notification_is_expired_property(self):
        """Test: is_expired property"""
        # Sin fecha de vencimiento: no expira
        self.assertFalse(self.notification.is_expired)
        
        # Fecha futura: no expirada
        self.notification.fecha_vencimiento = timezone.now() + timedelta(days=1)
        self.notification.save()
        self.assertFalse(self.notification.is_expired)
        
        # Fecha pasada: expirada
        self.notification.fecha_vencimiento = timezone.now() - timedelta(days=1)
        self.notification.save()
        self.assertTrue(self.notification.is_expired)
    
    def test_notification_is_unread_property(self):
        """Test: is_unread property"""
        self.assertTrue(self.notification.is_unread)
        
        self.notification.leida = True
        self.notification.save()
        self.assertFalse(self.notification.is_unread)
    
    def test_notification_requires_action_property(self):
        """Test: requires_action property"""
        # Info: no requiere acción
        self.notification.subtipo = 'info'
        self.notification.accionada = False
        self.assertFalse(self.notification.requires_action)
        
        # Critical sin accionar: requiere acción
        self.notification.subtipo = 'critical'
        self.notification.accionada = False
        self.notification.save()
        self.assertTrue(self.notification.requires_action)
        
        # Critical accionada: no requiere acción
        self.notification.accionada = True
        self.notification.save()
        self.assertFalse(self.notification.requires_action)
        
        # Warning sin accionar: requiere acción
        self.notification.subtipo = 'warning'
        self.notification.accionada = False
        self.notification.save()
        self.assertTrue(self.notification.requires_action)
    
    def test_notification_mark_as_read_method(self):
        """Test: mark_as_read() method"""
        self.assertFalse(self.notification.leida)
        
        self.notification.mark_as_read()
        
        self.assertTrue(self.notification.leida)
        self.assertFalse(self.notification.accionada)
    
    def test_notification_mark_as_actioned_method(self):
        """Test: mark_as_actioned() method"""
        self.assertFalse(self.notification.leida)
        self.assertFalse(self.notification.accionada)
        
        self.notification.mark_as_actioned()
        
        self.assertTrue(self.notification.leida)
        self.assertTrue(self.notification.accionada)
    
    def test_notification_with_task_relationship(self):
        """Test: Relación con Tarea"""
        self.assertEqual(self.notification.tarea_relacionada, self.tarea)
        
        # Tarea puede acceder a sus notificaciones
        notificaciones_tarea = self.tarea.notificaciones.all()
        self.assertIn(self.notification, notificaciones_tarea)
    
    def test_notification_with_project_relationship(self):
        """Test: Relación con Proyecto"""
        notification_project = Notification.objects.create(
            usuario=self.user,
            titulo='Notificación de Proyecto',
            mensaje='Mensaje',
            tipo='project',
            subtipo='info',
            proyecto_relacionado=self.proyecto
        )
        
        self.assertEqual(notification_project.proyecto_relacionado, self.proyecto)
        
        # Proyecto puede acceder a sus notificaciones
        notificaciones_proyecto = self.proyecto.notificaciones.all()
        self.assertIn(notification_project, notificaciones_proyecto)
    
    def test_notification_without_relationships(self):
        """Test: Notificación sin relaciones (system/achievement)"""
        notification_system = Notification.objects.create(
            usuario=self.user,
            titulo='Notificación del Sistema',
            mensaje='Mensaje del sistema',
            tipo='system',
            subtipo='info'
        )
        
        self.assertIsNone(notification_system.tarea_relacionada)
        self.assertIsNone(notification_system.proyecto_relacionado)
    
    def test_notification_business_context(self):
        """Test: JSONField business_context"""
        context = {
            'action': 'task_completed',
            'metadata': {'count': 5, 'date': '2025-11-16'}
        }
        
        self.notification.business_context = context
        self.notification.save()
        
        # Refrescar desde BD
        self.notification.refresh_from_db()
        
        self.assertEqual(self.notification.business_context['action'], 'task_completed')
        self.assertEqual(self.notification.business_context['metadata']['count'], 5)
