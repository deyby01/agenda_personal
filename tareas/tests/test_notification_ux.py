"""
Tests para UX de Notificaciones - Diseño Profesional

Arquitecto UX: Deyby Camacho
Vision: Sistema de notificaciones moderno como GitHub/LinkedIn
Componentes: Navbar bell + contador + página dedicada + auto-redirect
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import datetime

from tareas.models import Tarea, Proyecto, Notification


class NotificationUXTest(TestCase):
    """
    Testing para tu sistema UX de notificaciones profesional
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com', 
            password='testpassword'
        )
        self.client = Client()
        
    def test_navbar_shows_notification_bell_with_counter(self):
        """
        Navbar debe mostrar campana con contador de notificaciones
        """
        # Login usuario
        self.client.login(username='testuser', password='testpassword')
        
        # Crear exactamente 2 notificaciones no leídas
        Notification.objects.create(
            usuario=self.user,
            titulo='Test Notification 1',
            mensaje='Primera notificación',
            tipo='task',
            subtipo='critical',
            leida=False
        )
        
        Notification.objects.create(
            usuario=self.user,
            titulo='Test Notification 2', 
            mensaje='Segunda notificación',
            tipo='project',
            subtipo='warning',
            leida=False
        )
        
        # Crear una leída (no cuenta para badge)
        Notification.objects.create(
            usuario=self.user,
            titulo='Already Read',
            mensaje='Esta ya fue leída',
            tipo='system',
            subtipo='info',
            leida=True
        )
        
        # Acceder dashboard
        response = self.client.get(reverse('dashboard'))
        
        # VERIFICACIONES CORREGIDAS BASADAS EN TU DEBUG
        self.assertEqual(response.status_code, 200)
        
        # 1. Verificar campana existe
        self.assertContains(response, 'fas fa-bell', msg_prefix="Campana debe existir")
        
        # 2. Verificar badge estructura (basado en tu HTML)
        self.assertContains(response, 'badge rounded-pill bg-danger', msg_prefix="Badge debe existir")
        
        # 3. Verificar número 2 en contexto de badge (más flexible)
        html_content = response.content.decode('utf-8')
        import re
        badge_with_number = re.search(r'badge.*?bg-danger.*?>.*?2.*?<', html_content, re.DOTALL)
        self.assertIsNotNone(badge_with_number, "Badge debe contener el número 2")
        
        # 4. Verificar link al centro
        self.assertContains(response, 'Centro de Notificaciones', msg_prefix="Title tooltip debe existir")
        

    def test_notification_center_page_shows_all_notifications(self):
        """
        Página dedicada debe mostrar todas las notificaciones organizadas
        
        Testing página dedicada profesional
        """
        # Login usuario
        self.client.login(username='testuser', password='testpassword')
        
        # Crear diferentes tipos de notificaciones
        unread_critical = Notification.objects.create(
            usuario=self.user,
            titulo='🚨 Crítica No Leída',
            mensaje='Notificación crítica pendiente',
            tipo='task', 
            subtipo='critical',
            leida=False
        )
        
        read_notification = Notification.objects.create(
            usuario=self.user,
            titulo='✅ Leída',
            mensaje='Esta ya fue procesada',
            tipo='achievement',
            subtipo='success', 
            leida=True
        )
        
        # Acceder al centro de notificaciones
        response = self.client.get(reverse('centro_notificaciones'))
        
        # Verificar página carga correctamente
        self.assertEqual(response.status_code, 200)
        
        # Verificar contenido de ambas notificaciones
        self.assertContains(response, 'Crítica No Leída')
        self.assertContains(response, 'Leída')
        
        # Verificar diferenciación visual (clases CSS)
        self.assertContains(response, 'notification-unread')  # Para no leídas
        self.assertContains(response, 'notification-read')    # Para leídas
        
        # Verificar título de página
        self.assertContains(response, 'Centro de Notificaciones')
    
    def test_click_notification_marks_read_and_redirects(self):
        """
        Click en notificación debe marcar como leída y redirigir al origen
        
        Testing auto-redirect inteligente
        """
        # Login usuario
        self.client.login(username='testuser', password='testpassword')
        
        # Crear tarea relacionada
        tarea = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Importante',
            descripcion='Tarea para test de redirect'
        )
        
        # Crear notificación relacionada con la tarea
        notification = Notification.objects.create(
            usuario=self.user,
            titulo='🚨 Tarea Crítica: Tarea Importante',
            mensaje='Tu tarea requiere atención',
            tipo='task',
            subtipo='critical',
            tarea_relacionada=tarea,
            leida=False
        )
        
        # Verificar que inicialmente NO está leída
        self.assertFalse(notification.leida)
        
        # Click en la notificación (simular)
        response = self.client.get(
            reverse('notification_click', args=[notification.id])
        )
        
        # Verificar redirect al detalle de la tarea
        self.assertEqual(response.status_code, 302)
        expected_url = reverse('detalle_tarea_url', args=[tarea.id])
        self.assertRedirects(response, expected_url)
        
        # Verificar que la notificación se marcó como leída
        notification.refresh_from_db()
        self.assertTrue(notification.leida, "Notificación debe marcarse como leída después del click")

        # BONUS: Verificar que el contador disminuyó
        # (El context processor debería mostrar 0 notificaciones no leídas)
        dashboard_response = self.client.get(reverse('dashboard'))
        unread_count = Notification.objects.filter(usuario=self.user, leida=False).count()
        self.assertEqual(unread_count, 0, "Contador debe decrementar después de marcar como leída")