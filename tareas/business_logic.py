"""
Business Logic Layer - Domain rules and intelligence systems

Este modulo contiene las reglas de negocio complejas que definen
CÓMO funciona el dominio de gestion de tareas, no solo CÓMO acceder a datos.

Diferencias:
 -  Services: Calculos tecnicos (fechas, URLs, formateo)
 -  Business Logic: Reglas del dominio (priorizacion, alertas, recomendaciones)
 -  Repositories: Acceso a datos (queries, filtros)
"""

import datetime
from typing import List, Optional, Dict, Any, NamedTuple
from django.utils import timezone
from dataclasses import dataclass
from enum import Enum

from .models import Tarea, Proyecto
from .repositories import TareaRepository, ProyectoRepository


class PriorityLevel(Enum):
    """
    Niveles de prioridad para tareas
    """
    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'

class TaskUrgency(Enum):
    """
    Niveles de urgencia basados en tiempo
    """
    OVERDUE = 'overdue'
    DUE_TODAY = 'due_today'
    DUE_THIS_WEEK = 'due_this_week'
    DUE_NEXT_WEEK = 'due_next_week'
    NO_DEADLINE = 'no_deadline'



@dataclass
class TaskPriorityScore:
    """
    Value object que encapsula el score de prioridad de una tarea.
    """
    task_id: int
    priority_level: PriorityLevel
    urgency_level: TaskUrgency
    score: float
    reasons: List[str]

    @property
    def is_critical(self) -> bool:
        return self.priority_level == PriorityLevel.CRITICAL

    @property
    def needs_attention(self) -> bool:
        return self.score >= 7.0


class TaskPrioritizationEngine:
    """
    Motor inteligente de priorizacion de tareas.

    Implementa reglas de negocio complejas para determinar
    que tareas requieren atencion inmediata del usuario.

    Business Rules:
    1. Tareas vencidas = Prioridad critica
    2. Tareas con fecha hoy = Alta prioridad
    3. Tareas de proyectos importantes = +2 puntos
    4. Tareas sin completar por >7 dias = +1 punto
    5. Tareas con dependencias = +1 punto
    """

    # Business constants - configurable business rules
    OVERDUE_SCORE = 10.0
    DUE_TODAY_SCORE = 8.0
    DUE_THIS_WEEK_SCORE = 6.0
    DUE_NEXT_WEEK_SCORE = 4.0
    NO_DEADLINE_SCORE = 2.0

    IMPORTANT_PROJECT_BONUS = 2.0
    OLD_TASK_BONUS = 1.0
    HAS_DEPENDENCIES_BONUS = 1.0
    DAYS_THRESHOLD_OLD_TASK = 7

    @classmethod
    def calculate_priority_score(cls, tarea: Tarea) -> TaskPriorityScore:
        """
        Calcula el score de prioridad para una tarea especifica

        Args:
            tarea: Tarea a evaluar

        Returns:
            TaskPriorityScore con score calculado y razones 
        """
        score = 0.0
        reasons = []
        today = timezone.localdate()

        # 1. Evaluar urgencia por fecha
        urgency_level, urgency_score, urgency_reason = cls._calculate_urgency_score(tarea, today)
        score += urgency_score
        if urgency_reason:
            reasons.append(urgency_reason)

        # 2. Bonus por proyecto importante
        if tarea.proyecto and cls._is_important_project(tarea.proyecto):
            score += cls.IMPORTANT_PROJECT_BONUS
            reasons.append(f"Proyecto importante: {tarea.proyecto.nombre}")

        # 3. Bonus por tarea antigua
        if tarea.fecha_creacion and cls._is_old_task(tarea.fecha_creacion, today):
            score += cls.OLD_TASK_BONUS
            reasons.append(f"Tarea antigua (mas de {cls.DAYS_THRESHOLD_OLD_TASK} días)")

        # 4. Determinar nivel de prioridad
        priority_level = cls._score_to_priority_level(score)

        return TaskPriorityScore(
            task_id=tarea.id,
            priority_level=priority_level,
            urgency_level=urgency_level,
            score=score,
            reasons=reasons
        )

    @classmethod
    def _calculate_urgency_score(cls, tarea: Tarea, today: datetime.date) -> tuple[TaskUrgency, float, Optional[str]]:
        """ Calcula score basado en urgencia temporal """
        if not tarea.fecha_asignada:
            return TaskUrgency.NO_DEADLINE, cls.NO_DEADLINE_SCORE, 'Sin fecha limite'

        days_diff = (tarea.fecha_asignada - today).days

        if days_diff < 0:
            return TaskUrgency.OVERDUE, cls.OVERDUE_SCORE, f"Vencida hace {abs(days_diff)} días"
        elif days_diff == 0:
            return TaskUrgency.DUE_TODAY, cls.DUE_TODAY_SCORE, 'Vence hoy'
        elif days_diff <= 7:
            return TaskUrgency.DUE_THIS_WEEK, cls.DUE_THIS_WEEK_SCORE, f"Vence en {days_diff} días"
        elif days_diff <= 14:
            return TaskUrgency.DUE_NEXT_WEEK, cls.DUE_NEXT_WEEK_SCORE, f"Vence en {days_diff} días"
        else:
            return TaskUrgency.NO_DEADLINE, cls.NO_DEADLINE_SCORE, f"Vence en {days_diff} días"

    @classmethod
    def _is_important_project(cls, proyecto: Proyecto) -> bool:
        """
        Business rule: ¿Qué hace un proyecto importante?
        - Estado 'en_curso'
        - Tiene fecha de fin proxima
        - Multiples tareas asociadas
        """
        if proyecto.estado != 'en_curso':
            return False

        # Si tiene fecha de fin y es proxima (30 dias)
        if proyecto.fecha_fin_estimada:
            days_to_deadline = (proyecto.fecha_fin_estimada - timezone.localdate()).days
            if 0 <= days_to_deadline <= 30:
                return True

        # Si tiene muchas tareas (threshold configurable)
        task_count = proyecto.tareas.count()
        if task_count >= 5:
            return True

        return False

    @classmethod  
    def _is_old_task(cls, created_date: datetime.datetime, today: datetime.date) -> bool:
        """Business rule: ¿Cuándo una tarea es considerada antigua?"""
        created_date_only = created_date.date() if hasattr(created_date, 'date') else created_date
        days_old = (today - created_date_only).days
        return days_old > cls.DAYS_THRESHOLD_OLD_TASK


    @classmethod
    def _score_to_priority_level(cls, score: float) -> PriorityLevel:
        """ Mapea score numerico a nivel de prioridad categorico """
        if score >= 9.0:
            return PriorityLevel.CRITICAL
        elif score >= 7.0:
            return PriorityLevel.HIGH
        elif score >= 5.0:
            return PriorityLevel.MEDIUM
        else:
            return PriorityLevel.LOW

    @classmethod
    def prioritize_tasks(cls, tasks: List[Tarea]) -> List[TaskPriorityScore]:
        """
        Prioriza una lista de tareas y devuelve scores ordenados.

        Args:
            tasks: Lista de tareas a priorizar

        Returns:
            Lista de TaskPriorityScore ordenada por prioridad (mayor a menor)
        """
        priority_scores = [cls.calculate_priority_score(task) for task in tasks]
        return sorted(priority_scores, key=lambda x: x.score, reverse=True)



class ProjectProgressCalculator:
    """
    Calculadora avanzada de progreso de proyectos.

    Implementa business logic para calcular metricas
    inteligentes de progreso mas alla del simple porcentaje.  
    """

    @staticmethod
    def calculate_advanced_progress(proyecto: Proyecto) -> Dict[str, Any]:
        """
        Calcula metricas avanzadas de progreso del proyecto

        Returns:
            Dict con metricas calculadas:
            - completion_percentage: Porcentaje basico
            - velocity: Tareas completadas por dia
            - estimated_completion: Fecha estimada de finalizacion
            - health_status: Estado de salud del proyecto
            - critical_path: Tareas criticas para la finalizacion
        """
        all_tasks = proyecto.tareas.all()
        completed_tasks = all_tasks.filter(completada=True)
        pending_tasks = all_tasks.filter(completada=False)

        total_count = all_tasks.count()
        completed_count = completed_tasks.count()

        # Calculo basico
        completion_percentage = (completed_count / total_count * 100) if total_count > 0 else 0

        # Calculo de velocidad (business logic)
        velocity = ProjectProgressCalculator._calculate_velocity(proyecto, completed_tasks)

        # Estimacion de finalizacion
        estimated_completion = ProjectProgressCalculator._estimate_completion_date(
            pending_tasks.count(), velocity, proyecto.fecha_fin_estimada
        )

        # Estado de salud del proyecto
        health_status = ProjectProgressCalculator._assess_project_health(
            completion_percentage, estimated_completion, proyecto.fecha_fin_estimada
        )

        # Tareas criticas
        critical_tasks = ProjectProgressCalculator._identify_critical_tasks(pending_tasks)

        return {
            'completion_percentage': round(completion_percentage, 1),
            'velocity': round(velocity, 2),
            'estimated_completion': estimated_completion,
            'health_status': health_status,
            'critical_tasks': critical_tasks,
            'total_tasks': total_count,
            'completed_tasks': completed_count,
            'pending_tasks': pending_tasks.count()
        }

    @staticmethod
    def _calculate_velocity(proyecto: Proyecto, completed_tasks) -> float:
        """ Calcula tareas completadas por dia en los ultimos 30 dias """
        thirty_days_ago = timezone.now() - datetime.timedelta(days=30)
        recent_completions = completed_tasks.filter(
            fecha_creacion__gte=thirty_days_ago
        ).count()

        return recent_completions / 30.0 # Tasks per day

    @staticmethod
    def _estimate_completion_date(pending_count: int, velocity: float, planned_end: Optional[datetime.date]) -> Optional[datetime.date]:
        """ Estima fecha de finalizacion basada en velocidad actual """
        if velocity <= 0:
            return None

        days_needed = pending_count / velocity
        estimated_date = timezone.localdate() + datetime.timedelta(days=int(days_needed))

        return estimated_date

    @staticmethod
    def _assess_project_health(completion_percentage: float, estimated_completion: Optional[datetime.date], planned_end: Optional[datetime.date]) -> str:
        """ Business rule: Evalua estado de salud del proyecto """
        if completion_percentage >= 90:
            return "excellent"
        elif completion_percentage >= 70:
            return "good"
        elif completion_percentage >= 50:
            return "fair"
        elif completion_percentage >= 25:
            return "poor"
        else:
            return "critical"

    @staticmethod
    def _identify_critical_tasks(pending_tasks) -> List[Dict[str, Any]]:
        """ Identifica tareas criticas para la finalizacion del proyecto """
        # Business logic: tareas con fecha proxima o sin fecha
        critical = []
        today = timezone.localdate()

        for task in pending_tasks[:5]: # Top 5 critical
            criticality_reason = []

            if task.fecha_asignada:
                days_left = (task.fecha_asignada - today).days
                if days_left <= 3:
                    criticality_reason.append('Vence pronto')
                elif days_left < 0:
                    criticality_reason.append('Vencido')
            else:
                criticality_reason.append('Sin fecha limite')

            critical.append({
                'task': task,
                'reasons': criticality_reason
            })

        return critical