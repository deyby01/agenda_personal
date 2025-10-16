"""
Servicio de Notificaciones Inteligentes

Arquitecto: Deyby Camacho
Principios SOLID aplicados:
- SRP: Una responsabilidad = generar notificaciones
- OCP: Extensible para nuevos tipos de alertas
- DIP: Depende de abstracciones, no implementaciones

Integración: TaskPrioritizationEngine + ProjectProgressCalculator
"""
from typing import List, Dict, Optional
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

from .models import Notification, Tarea, Proyecto
from .business_logic import TaskPrioritizationEngine, ProjectProgressCalculator, PriorityLevel


class NotificationService:
    """
    Servicio principal para generar notificaciones inteligentes
    
    SRP: SOLO se encarga de crear y gestionar notificaciones
    OCP: Fácil agregar nuevos tipos de análisis sin modificar código existente
    """
    
    @staticmethod
    def generate_task_notifications(usuario: User) -> List[Notification]:
        """
        Genera notificaciones basadas en análisis de tareas
        
        Usa tu TaskPrioritizationEngine para detectar situaciones críticas
        """
        notifications_created = []
        
        # Obtener tareas del usuario
        user_tasks = Tarea.objects.filter(usuario=usuario)
        if not user_tasks.exists():
            return notifications_created
        
        # USAR TU BUSINESS LOGIC 🚀
        prioritized_tasks = TaskPrioritizationEngine.prioritize_tasks(user_tasks)
        
        # Analizar cada tarea priorizada
        for task_score in prioritized_tasks:
            task = Tarea.objects.get(id=task_score.task_id)
            
            # CRÍTICO: Generar notificación si la tarea es crítica
            if task_score.priority_level == PriorityLevel.CRITICAL:
                notification = NotificationService._create_critical_task_notification(
                    usuario=usuario,
                    tarea=task, 
                    task_score=task_score
                )
                if notification:
                    notifications_created.append(notification)
        
        return notifications_created
    
    @staticmethod
    def generate_project_notifications(usuario: User) -> List[Notification]:
        """
        Genera notificaciones basadas en salud de proyectos
        
        Usa tu ProjectProgressCalculator para detectar riesgos
        """
        notifications_created = []
        
        # Obtener proyectos del usuario  
        user_projects = Proyecto.objects.filter(usuario=usuario)
        
        for proyecto in user_projects:
            # USAR TU BUSINESS LOGIC 🚀
            progress_data = ProjectProgressCalculator.calculate_advanced_progress(proyecto)
            
            # CRÍTICO: Proyecto en estado crítico
            if progress_data['health_status'] == 'critical':
                notification = NotificationService._create_critical_project_notification(
                    usuario=usuario,
                    proyecto=proyecto,
                    progress_data=progress_data
                )
                if notification:
                    notifications_created.append(notification)
        
        return notifications_created
    
    @staticmethod
    def _create_critical_task_notification(usuario: User, tarea: Tarea, task_score) -> Optional[Notification]:
        """
        Crea notificación específica para tarea crítica
        
        Lógica anti-duplicados robusta para producción y tests
        """
        # LÓGICA MEJORADA: Verificar duplicados con query más específica
        today = timezone.now().date()
        
        # Buscar notificación existente hoy para esta tarea específica
        existing = Notification.objects.filter(
            usuario=usuario,
            tarea_relacionada=tarea,
            tipo='task',
            subtipo='critical',
            fecha_creacion__date=today
        ).first()  # ← Usar .first() en lugar de .exists() para más información
        
        if existing:
            return None
        
        # DEBUGGING: Verificar estado antes de crear
        all_notifications_for_task = Notification.objects.filter(
            tarea_relacionada=tarea
        )
        
        # Crear nueva notificación
        reasons_text = ', '.join(task_score.reasons) if task_score.reasons else 'Análisis de prioridad'
        
        notification = Notification.objects.create(
            usuario=usuario,
            titulo=f'🚨 Tarea Crítica: {tarea.titulo}',
            mensaje=f'Tu tarea "{tarea.titulo}" requiere atención inmediata. '
                f'Razones: {reasons_text}. '
                f'Prioridad calculada: {task_score.score:.1f}/10',
            tipo='task',
            subtipo='critical',
            tarea_relacionada=tarea,
            business_context={
                'priority_score': task_score.score,
                'priority_level': str(task_score.priority_level),
                'urgency_level': str(task_score.urgency_level), 
                'reasons': task_score.reasons,
                'generated_by': 'TaskPrioritizationEngine'
            }
        )
        return notification




    
    @staticmethod  
    def _create_critical_project_notification(usuario: User, proyecto: Proyecto, progress_data: Dict) -> Optional[Notification]:
        """
        Crea notificación específica para proyecto crítico
        
        SRP: SOLO crear notificación de proyecto crítico
        """
        # Evitar duplicados
        existing = Notification.objects.filter(
            usuario=usuario,
            proyecto_relacionado=proyecto,
            subtipo='critical',
            fecha_creacion__date=timezone.now().date()
        ).exists()
        
        if existing:
            return None
        
        notification = Notification.objects.create(
            usuario=usuario,
            titulo=f'🚨 Proyecto Crítico: {proyecto.nombre}',
            mensaje=f'Tu proyecto "{proyecto.nombre}" está en estado crítico. '
                   f'Progreso: {progress_data["completion_percentage"]}%. '
                   f'Necesita revisión inmediata para evitar retrasos.',
            tipo='project',
            subtipo='critical', 
            proyecto_relacionado=proyecto,
            business_context={
                'health_status': progress_data['health_status'],
                'completion_percentage': progress_data['completion_percentage'],
                'velocity': progress_data['velocity'],
                'total_tasks': progress_data['total_tasks'],
                'generated_by': 'ProjectProgressCalculator'
            }
        )
        
        return notification
    
    @staticmethod
    def generate_daily_notifications(usuario: User) -> List[Notification]:
        """
        Genera todas las notificaciones diarias para un usuario
        
        OCP: Fácil agregar nuevos tipos de análisis aquí
        """
        all_notifications = []
        
        # Generar notificaciones de tareas
        task_notifications = NotificationService.generate_task_notifications(usuario)
        all_notifications.extend(task_notifications)
        
        # Generar notificaciones de proyectos
        project_notifications = NotificationService.generate_project_notifications(usuario)
        all_notifications.extend(project_notifications)
        
        # TODO: Futuros tipos de notificaciones (achievements, reminders, etc.)
        
        return all_notifications
