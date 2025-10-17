"""
Este modulo implementa el patron Service Layer para separar la logica de negocio de las vistas.
"""
import datetime
from django.utils import timezone
from django.urls import reverse
from typing import Dict, List, Optional, Tuple, NamedTuple

class WeekRange(NamedTuple):
    """
    Value Object para representar un rango de semanas.
    """
    start_date: datetime.date
    end_date: datetime.date

    @property
    def days(self) -> List[datetime.date]:
        """ Obtiene lista de los dias de la semana """
        return [self.start_date + datetime.timedelta(days=i) for i in range(7)]

    @property
    def is_current_week(self) -> bool:
        """ Verificar si este rango incluye el dia actual """
        today = timezone.localdate()
        return self.start_date <= today <= self.end_date

    def format_display(self) -> str:
        """ Formatea el rango para mostrar en UI """
        if self.start_date.month == self.end_date.month:
            return f"{self.start_date.strftime('%d')} - {self.end_date.strftime('%d %b %Y')}"
        return f"{self.start_date.strftime('%d %b')} - {self.end_date.strftime('%d %b %Y')}"


class WeekCalculatorService:
    """
    Servicio para calculos relacionados con semanas.

    Single Responsability: SOLO maneja logica de fechas y semanas.
    - No conoce sobre Django views
    - No conoce sobre modelos de datos
    - No maneja URLs o navegacion

    Esto permite:
    - Testing independiente
    - Reutilizacion en diferentes contextos
    - Cambios en logica de fechas sin afectar otros componentes
    """

    @staticmethod
    def get_week_range(base_date: Optional[datetime.date] = None) -> WeekRange:
        """
        Calcula el rango de semana para una fecha dada.

        Args:
            base_date: Fecha base (si None, usa fecha actual)
        Returns:
            WeekRange con inicio (lunes) y fin (domingo) de la semana
        """
        if base_date is None:
            base_date = timezone.localdate()

        # Calcular lunes de la semana (weekday 0 = lunes)
        start_week = base_date - datetime.timedelta(days=base_date.weekday())
        # Calcular domingo de la semana
        end_week = start_week + datetime.timedelta(days=6)

        return WeekRange(start_week, end_week)

    @staticmethod
    def get_navigation_weeks(current_week: WeekRange) -> Dict[str, WeekRange]:
        """
        Obtiene la semana anterior  y siguiente para navegacion.

        Args:
            current_week: Semana actual
        Returns:
            Dict con keys 'previous' y 'next' conteniendo WeekRange
        """
        previous_start = current_week.start_date - datetime.timedelta(days=7)
        next_start = current_week.start_date + datetime.timedelta(days=7)

        return {
            'previous': WeekCalculatorService.get_week_range(previous_start),
            'next': WeekCalculatorService.get_week_range(next_start)
        }

    
    @staticmethod
    def parse_date_params(year: Optional[int], month: Optional[int], day: Optional[int]) -> datetime.date:
        """
        Parsea parametros de URL a fecha valida

        Args:
            year, month, day: Parametros opcionales de fecha
        Returns:
            Fecha valida (usa hoy si paramtros son None)
        
        Raises: 
            ValueError: Si la fecha es invalida
        """
        if all(param is not None for param in [year, month, day]):
            try:
                return datetime.date(year, month, day)
            except ValueError:
                # Fecha invalidad usar fecha actual
                return timezone.localdate()
        
        return timezone.localdate()


class WeekNavigationService:
    """
    Servicio para generar URLs de navegacion de semana.

    Single Responsability: SOLO maneja generacion de URLs
    Separado de WeekCalculatorService porque:
    - Tiene diferentes razones para cambiar (URLs vs logica de fechas)
    - Depende del sistema de ruteo de Django
    - Puede necesitar diferentes estrategias de URL
    """

    @staticmethod
    def get_navigation_urls(current_week: WeekRange, navigation_weeks: Dict[str, WeekRange]) -> Dict[str, Optional[str]]:
        """
        Genera URLs para navegacion de semanas.

        Args:
            current_week: Semana actual.
            navigation_weeks: Dict con semanas 'previous' y 'next'
        Returns:
            Dict con URLs de navegacion ('previous' puede ser None si es semana actual)
        """
        urls = {}

        # URL semana anterior (None si es semana actual)
        if current_week.is_current_week:
            urls['previous'] = None
        else:
            prev_week = navigation_weeks['previous']
            urls['previous'] = reverse(
                'mi_semana_especifica_url',
                args=[prev_week.start_date.year, prev_week.start_date.month, prev_week.start_date.day]
            )

        # URL semana siguiente
        next_week = navigation_weeks['next']
        urls['next'] = reverse(
            'mi_semana_especifica_url',
            args=[next_week.start_date.year, next_week.start_date.month, next_week.start_date.day]
        )

        # URL semana actual
        urls['current'] = reverse('mi_semana_actual_url')

        return urls

    @staticmethod
    def get_create_task_urls(week_range: WeekRange) -> Dict[str, str]:
        """
        Genera URLs para crear tareas en dias especificos.

        Args:
            week_range: Rango de semana
        Returns:
            Dict con URLs para crear tareas por dia
        """
        urls = {}
        for day in week_range.days:
            day_key = day.strftime('%A').lower() # monday, tuesday, etc
            urls[day_key] = f"{reverse('crear_tarea_url')}?fecha_asignada={day.strftime('%Y-%m-%d')}"
        
        return urls