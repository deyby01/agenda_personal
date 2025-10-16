"""
Test para el sistema de notificaciones inteligentes

Fecha: 15-10-2025
"""
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

from tareas.business_logic import TaskPrioritizationEngine
from tareas.models import Tarea, Proyecto, Notification
from tareas.notification_service import NotificationService

class NotificationModelTest(TestCase):
    """
    Pruebas para el modelo de notificaciones
    """

    def setUp(self):
        """ Configurar datos de prueba """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )

        # Crear tarea para referencias
        self.tarea = Tarea.objects.create(
            usuario = self.user,
            titulo = 'Tarea test',
            fecha_asignada = timezone.now().date()
        )

        # Navegador falso
        self.client = Client()

    def test_create_notification(self):
        """
        Probar creacion de notificacion 
        """
        # Crear notificacion critica relacionada con tarea
        notification = Notification.objects.create(
            usuario = self.user,
            titulo = 'Tarea Crítica Detectada',
            mensaje = 'La tarea "Tarea test" requiere atencion inmediata segun el analisis de prioridad',
            tipo = 'task',
            subtipo = 'critical',
            tarea_relacionada = self.tarea,
            business_context = {
                'priority_score': 9.5,
                'days_overdue': 2,
                'analysis_engine': 'TaskPrioritizationEngine'
            },
        )

        # ===== Verificaciones del modelo =====
        # Campos basicos
        self.assertEqual(notification.usuario, self.user)
        self.assertEqual(notification.titulo, 'Tarea Crítica Detectada')
        self.assertEqual(notification.tipo, 'task')
        self.assertEqual(notification.subtipo, 'critical')

        # Estados por defecto
        self.assertFalse(notification.leida)
        self.assertFalse(notification.accionada)

        # Relaciones
        self.assertEqual(notification.tarea_relacionada, self.tarea)
        self.assertIsNone(notification.proyecto_relacionado)

        # Metadata automatica
        self.assertIsNotNone(notification.fecha_creacion)

        # Business context 
        self.assertEqual(notification.business_context['priority_score'], 9.5)

        # Metodos del modelo
        self.assertEqual(notification.urgency_icon, '🚨')
        self.assertFalse(notification.is_expired) # No fecha vencimiento

        # String representation
        expected_str = f"Tarea Crítica Detectada ({self.user.username})"
        self.assertEqual(str(notification), expected_str)

    def test_notification_types_and_subtypes(self):
        """
        Probar los diferentes tipos y subipos de notificaciones
        Verificando sistema de clasificación.
        """
        # Notificacion de proyecto en riesgo.
        project_notification = Notification.objects.create(
            usuario=self.user,
            titulo='Proyecto en Riesgo',
            mensaje='El proyecto necesita atención.',
            tipo='project',
            subtipo='warning'
        )

        # Notificacion de logro
        success_notification = Notification.objects.create(
            usuario=self.user,
            titulo='¡Proyecto Completado!',
            mensaje='Has completado exitosamente un proyecto.',
            tipo='achivement',
            subtipo='success'
        )

        # Verificar iconos apropiados
        self.assertEqual(project_notification.urgency_icon, '⚠️')
        self.assertEqual(success_notification.urgency_icon, '✅')

        # Verificar clasificación
        self.assertEqual(project_notification.tipo, 'project')
        self.assertEqual(success_notification.tipo, 'achivement')

    def test_notification_service_generates_critical_task_alerts(self):
        """
        El servicio debe generar notificaciones automáticamente para tareas críticas
        
        Testing integración con tu TaskPrioritizationEngine
        """
        # Crear tarea vencida (debería ser crítica)
        today = timezone.now().date()
        critical_task = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Vencida Crítica',
            descripcion='Esta tarea debería generar notificación',
            fecha_asignada=today - datetime.timedelta(days=3)  # 3 días vencida
        )
        
        # Generar notificaciones usando business logic
        notifications = NotificationService.generate_task_notifications(self.user)
        
        # Verificar que se generó notificación
        self.assertGreater(len(notifications), 0, "Debería generar al menos una notificación")
        
        # Verificar que es del tipo correcto
        critical_notification = notifications[0]
        self.assertEqual(critical_notification.tipo, 'task')
        self.assertEqual(critical_notification.subtipo, 'critical')
        self.assertEqual(critical_notification.tarea_relacionada, critical_task)
        
        # Verificar contexto de business logic
        self.assertIsNotNone(critical_notification.business_context)
        self.assertIn('priority_score', critical_notification.business_context)
        self.assertEqual(critical_notification.business_context['generated_by'], 'TaskPrioritizationEngine')

    def test_notification_service_no_duplicates_same_day(self):
        """
        No debe crear notificaciones duplicadas el mismo día
        """
        # Crear tarea crítica
        today = timezone.now().date()
        critical_task = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea para Duplicados Test',
            fecha_asignada=today - datetime.timedelta(days=2)
        )
        
        from tareas.notification_service import NotificationService
        
        # PRIMERA LLAMADA: Generar notificaciones
        first_batch = NotificationService.generate_task_notifications(self.user)
        first_count = len(first_batch)
        
        # VERIFICAR: Notificación se creó en base de datos
        notifications_in_db = Notification.objects.filter(
            usuario=self.user,
            tarea_relacionada=critical_task,
            tipo='task',
            subtipo='critical'
        )
        self.assertEqual(notifications_in_db.count(), 1, "Primera notificación debe estar en DB")
        
        # SEGUNDA LLAMADA: Intentar generar duplicados (mismo día)
        second_batch = NotificationService.generate_task_notifications(self.user)
        
        # NO debe crear nuevas notificaciones
        self.assertEqual(len(second_batch), 0, "No debe crear notificaciones duplicadas el mismo día")
        
        # VERIFICAR: Solo debe existir UNA notificación total en BD
        total_notifications = Notification.objects.filter(
            usuario=self.user,
            tarea_relacionada=critical_task,
            tipo='task',
            subtipo='critical'
        ).count()
        
        self.assertEqual(total_notifications, 1, "Solo debe existir una notificación por tarea por día")



