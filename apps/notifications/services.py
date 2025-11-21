"""
Notification Services - Business Logic Layer.

Lógica de negocio para creación y gestión de notificaciones.

Migrado desde tareas/notification_service.py con mejoras.
Integración con TaskPrioritizationEngine y ProjectProgressCalculator.
"""

from typing import Dict, List, Optional
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from apps.notifications.models import Notification
from apps.tasks.models import Tarea
from apps.projects.models import Proyecto
from apps.tasks.business_logic import (
    TaskPrioritizationEngine,
    ProjectProgressCalculator,
    PriorityLevel
)


class NotificationService:
    """
    Servicio para creación y gestión de notificaciones.
    
    Single Responsibility: Lógica de negocio de notificaciones.
    
    Features:
    - Crear notificaciones simples (task, project, achievement)
    - Generar notificaciones inteligentes (usando business logic)
    - Detectar tareas críticas
    - Monitorear salud de proyectos
    - Evitar duplicados
    """
    
    # ========== MÉTODOS SIMPLES (CRUD) ==========
    
    @staticmethod
    def create_task_notification(
        user: User,
        tarea: Tarea,
        titulo: str,
        mensaje: str,
        subtipo: str = 'info'
    ) -> Notification:
        """
        Crea notificación relacionada a una tarea.
        
        Args:
            user: Usuario que recibe la notificación
            tarea: Tarea relacionada
            titulo: Título de la notificación
            mensaje: Mensaje de la notificación
            subtipo: Subtipo de urgencia (info, warning, critical, success)
            
        Returns:
            Notification: Notificación creada
        """
        return Notification.objects.create(
            usuario=user,
            titulo=titulo,
            mensaje=mensaje,
            tipo='task',
            subtipo=subtipo,
            tarea_relacionada=tarea
        )
    
    @staticmethod
    def create_project_notification(
        user: User,
        proyecto: Proyecto,
        titulo: str,
        mensaje: str,
        subtipo: str = 'info'
    ) -> Notification:
        """
        Crea notificación relacionada a un proyecto.
        
        Args:
            user: Usuario que recibe la notificación
            proyecto: Proyecto relacionado
            titulo: Título de la notificación
            mensaje: Mensaje de la notificación
            subtipo: Subtipo de urgencia
            
        Returns:
            Notification: Notificación creada
        """
        return Notification.objects.create(
            usuario=user,
            titulo=titulo,
            mensaje=mensaje,
            tipo='project',
            subtipo=subtipo,
            proyecto_relacionado=proyecto
        )
    
    @staticmethod
    def create_overdue_task_notification(tarea: Tarea) -> Notification:
        """
        Crea notificación para tarea atrasada.
        
        Args:
            tarea: Tarea atrasada
            
        Returns:
            Notification: Notificación creada
        """
        return Notification.objects.create(
            usuario=tarea.usuario,
            titulo=f"Tarea Atrasada: {tarea.titulo}",
            mensaje=f"La tarea '{tarea.titulo}' estaba programada para {tarea.fecha_asignada} y aún no está completada.",
            tipo='task',
            subtipo='warning',
            tarea_relacionada=tarea,
            business_context={
                'dias_atrasada': (timezone.localdate() - tarea.fecha_asignada).days,
                'fecha_asignada': str(tarea.fecha_asignada)
            }
        )
    
    @staticmethod
    def create_achievement_notification(
        user: User,
        titulo: str,
        mensaje: str,
        context: Optional[Dict] = None
    ) -> Notification:
        """
        Crea notificación de logro.
        
        Args:
            user: Usuario que recibe el logro
            titulo: Título del logro
            mensaje: Mensaje descriptivo
            context: Contexto adicional (opcional)
            
        Returns:
            Notification: Notificación de logro creada
        """
        return Notification.objects.create(
            usuario=user,
            titulo=titulo,
            mensaje=mensaje,
            tipo='achievement',
            subtipo='success',
            business_context=context,
            fecha_vencimiento=timezone.now() + timedelta(days=7)
        )
    
    # ========== MÉTODOS INTELIGENTES (Business Logic) ==========
    
    @staticmethod
    def generate_task_notifications(usuario: User) -> List[Notification]:
        """
        Genera notificaciones basadas en análisis de tareas.
        
        Usa TaskPrioritizationEngine para detectar situaciones críticas.
        
        Args:
            usuario: Usuario propietario
            
        Returns:
            List[Notification]: Notificaciones creadas
        """
        notifications_created = []
        
        # Obtener tareas del usuario
        user_tasks = Tarea.objects.filter(usuario=usuario)
        if not user_tasks.exists():
            return notifications_created
        
        # USAR BUSINESS LOGIC 🚀
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
        Genera notificaciones basadas en salud de proyectos.
        
        Usa ProjectProgressCalculator para detectar riesgos.
        
        Args:
            usuario: Usuario propietario
            
        Returns:
            List[Notification]: Notificaciones creadas
        """
        notifications_created = []
        
        # Obtener proyectos del usuario
        user_projects = Proyecto.objects.filter(usuario=usuario)
        
        for proyecto in user_projects:
            # USAR BUSINESS LOGIC 🚀
            progress_data = ProjectProgressCalculator.calculate_advanced_progress(
                proyecto
            )
            
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
    def _create_critical_task_notification(
        usuario: User,
        tarea: Tarea,
        task_score
    ) -> Optional[Notification]:
        """
        Crea notificación específica para tarea crítica.
        
        Evita duplicados (24 horas y diarios).
        
        Args:
            usuario: Usuario propietario
            tarea: Tarea crítica
            task_score: Score de prioridad
            
        Returns:
            Optional[Notification]: Notificación creada o None si duplicada
        """
        today = timezone.now().date()
        
        # === DETECCIÓN DE DUPLICADOS ===
        
        # Búsqueda 1: Notificaciones de hoy para esta tarea
        existing_today = Notification.objects.filter(
            usuario=usuario,
            tarea_relacionada=tarea,
            tipo='task',
            subtipo='critical',
            fecha_creacion__date=today
        ).first()
        
        if existing_today:
            return None  # No crear duplicado
        
        # Búsqueda 2: Notificaciones en las últimas 24 horas
        last_24h = timezone.now() - timedelta(hours=24)
        recent_notifications = Notification.objects.filter(
            usuario=usuario,
            tarea_relacionada=tarea,
            tipo='task',
            subtipo='critical',
            fecha_creacion__gte=last_24h
        ).count()
        
        if recent_notifications > 0:
            return None
        
        # Crear notificación
        reasons_text = ', '.join(
            task_score.reasons
        ) if task_score.reasons else 'Análisis de prioridad'
        
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
    def _create_critical_project_notification(
        usuario: User,
        proyecto: Proyecto,
        progress_data: Dict
    ) -> Optional[Notification]:
        """
        Crea notificación específica para proyecto crítico.
        
        SRP: SOLO crear notificación de proyecto crítico.
        
        Args:
            usuario: Usuario propietario
            proyecto: Proyecto crítico
            progress_data: Datos de progreso calculados
            
        Returns:
            Optional[Notification]: Notificación creada o None si duplicada
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
        Genera todas las notificaciones diarias para un usuario.
        
        OCP: Fácil agregar nuevos tipos de análisis aquí.
        
        Args:
            usuario: Usuario propietario
            
        Returns:
            List[Notification]: Todas las notificaciones generadas
        """
        all_notifications = []
        
        # Generar notificaciones de tareas
        task_notifications = NotificationService.generate_task_notifications(
            usuario
        )
        all_notifications.extend(task_notifications)
        
        # Generar notificaciones de proyectos
        project_notifications = NotificationService.generate_project_notifications(
            usuario
        )
        all_notifications.extend(project_notifications)
        
        # TODO: Futuros tipos de notificaciones (achievements, reminders, etc.)
        
        return all_notifications
