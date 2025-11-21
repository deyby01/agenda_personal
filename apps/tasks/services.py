"""
Task Services - Business Logic Layer.

Migrado desde tareas/services.py
Contiene: WeekCalculatorService, WeekNavigationService

NOTA: Mantiene AMBAS APIs (antigua y nueva) para compatibilidad.
"""

import datetime
from typing import Dict, List, Optional, Tuple
from django.utils import timezone
from django.urls import reverse, NoReverseMatch

from apps.core.utils import WeekRange


class WeekCalculatorService:
    """
    Servicio para cálculos relacionados con semanas.
    
    Single Responsibility: Cálculos de fechas y rangos de semana.
    
    IMPORTANTE: Mantiene dos APIs diferentes para compatibilidad:
    - API antigua (date-based): parse_date_params(year, month, day)
    - API nueva (week-based): parse_week_params(year_param, week_param)
    """
    
    # ========== API NUEVA (week-based) ==========
    
    @staticmethod
    def get_week_range_from_week_number(
        year: Optional[int] = None,
        week: Optional[int] = None
    ) -> WeekRange:
        """
        Obtiene rango de semana usando número de semana ISO.
        
        API NUEVA: Usa year/week number (ISO 8601)
        
        Args:
            year: Año (default: año actual)
            week: Número de semana ISO (default: semana actual)
            
        Returns:
            WeekRange: Objeto con start_date y end_date
        """
        if year is None or week is None:
            today = timezone.localdate()
            year = today.year
            week = today.isocalendar()[1]
        
        # Calcular lunes de la semana
        jan_4 = datetime.date(year, 1, 4)
        week_1_monday = jan_4 - datetime.timedelta(days=jan_4.weekday())
        monday = week_1_monday + datetime.timedelta(weeks=week - 1)
        
        # Calcular domingo
        sunday = monday + datetime.timedelta(days=6)
        
        return WeekRange(start_date=monday, end_date=sunday)
    
    @staticmethod
    def parse_week_params(
        year_param: Optional[str],
        week_param: Optional[str]
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        Parsea parámetros de año y semana de URL.
        
        API NUEVA: Para URLs como /semana/2025/47/
        
        Args:
            year_param: Año como string
            week_param: Semana como string
            
        Returns:
            Tuple (year, week) o (None, None) si inválidos
        """
        try:
            year = int(year_param) if year_param else None
            week = int(week_param) if week_param else None
            return year, week
        except (ValueError, TypeError):
            return None, None
    
    # ========== API ANTIGUA (date-based) - COMPATIBILIDAD ==========
    
    @staticmethod
    def get_week_range(base_date: Optional[datetime.date] = None) -> WeekRange:
        """
        Calcula el rango de semana para una fecha dada.
        
        API ANTIGUA: Usa datetime.date como base
        MANTIENE COMPATIBILIDAD con código existente.
        
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
        
        return WeekRange(start_date=start_week, end_date=end_week)
    
    @staticmethod
    def parse_date_params(
        year: Optional[int],
        month: Optional[int],
        day: Optional[int]
    ) -> datetime.date:
        """
        Parsea parámetros de URL a fecha válida.
        
        API ANTIGUA: Para URLs como /mi-semana/2025/11/20/
        MANTIENE COMPATIBILIDAD con tareas/views.py existente.
        
        Args:
            year, month, day: Parámetros opcionales de fecha
            
        Returns:
            Fecha válida (usa hoy si parámetros son None)
            
        Raises:
            ValueError: Si la fecha es inválida
        """
        if all(param is not None for param in [year, month, day]):
            try:
                return datetime.date(year, month, day)
            except ValueError:
                # Fecha inválida, usar fecha actual
                return timezone.localdate()
        
        return timezone.localdate()
    
    # ========== MÉTODOS COMPARTIDOS ==========
    
    @staticmethod
    def get_navigation_weeks(current_week: WeekRange) -> Dict[str, WeekRange]:
        """
        Obtiene la semana anterior y siguiente para navegación.
        
        COMPATIBLE con ambas APIs.
        
        Args:
            current_week: Semana actual
            
        Returns:
            Dict con keys 'previous' (o 'prev') y 'next' conteniendo WeekRange
        """
        previous_start = current_week.start_date - datetime.timedelta(days=7)
        next_start = current_week.start_date + datetime.timedelta(days=7)
        
        return {
            'previous': WeekCalculatorService.get_week_range(previous_start),
            'prev': WeekCalculatorService.get_week_range(previous_start),  # Alias
            'next': WeekCalculatorService.get_week_range(next_start)
        }


class WeekNavigationService:
    """
    Servicio para generar URLs de navegación entre semanas.
    
    Single Responsibility: Generación de URLs de navegación.
    
    MANTIENE COMPATIBILIDAD con ambas APIs de URL.
    """
    
    @staticmethod
    def get_navigation_urls(
        current_week: WeekRange,
        navigation_weeks: Optional[Dict[str, WeekRange]] = None,
        url_name: str = 'mi_semana_especifica_url'
    ) -> Dict[str, str]:
        """
        Genera URLs de navegación (prev/next week).
        
        COMPATIBLE con ambas APIs:
        - API antigua: /mi-semana/<year>/<month>/<day>/
        - API nueva: /semana/<year>/<week>/
        
        Args:
            current_week: Semana actual
            navigation_weeks: Dict con semanas prev/next (opcional)
            url_name: Nombre de la URL de Django
            
        Returns:
            Dict con 'previous' y 'next' (URLs)
        """
        # Calcular navigation_weeks si no se proporciona
        if navigation_weeks is None:
            navigation_weeks = WeekCalculatorService.get_navigation_weeks(current_week)
        
        prev_week = navigation_weeks.get('previous') or navigation_weeks.get('prev')
        next_week = navigation_weeks.get('next')
        
        # Generar URLs usando la API nueva (year/week) o la antigua (anio/mes/dia)
        prev_date = prev_week.start_date if prev_week else current_week.start_date
        next_date = next_week.start_date if next_week else current_week.start_date
        
        return {
            'previous': WeekNavigationService._build_week_url(url_name, prev_date),
            'next': WeekNavigationService._build_week_url(url_name, next_date),
        }

    @staticmethod
    def _build_week_url(url_name: str, date_obj: datetime.date) -> str:
        """
        Intenta generar URL usando la API nueva (year/week) y
        si falla, recurre a la API antigua (anio/mes/dia).
        """
        iso_year, iso_week, _ = date_obj.isocalendar()
        
        # Intentar API nueva (year/week)
        try:
            return reverse(url_name, kwargs={
                'year': iso_year,
                'week': iso_week,
            })
        except NoReverseMatch:
            pass
        
        # Fallback API antigua (anio/mes/dia)
        return reverse(url_name, kwargs={
            'anio': date_obj.year,
            'mes': date_obj.month,
            'dia': date_obj.day,
        })
    
    @staticmethod
    def get_create_task_urls(
        week_range: WeekRange,
        url_name: str = 'crear_tarea_url'
    ) -> Dict[str, str]:
        """
        Genera URLs para crear tareas por cada día de la semana.
        
        Args:
            week_range: Semana actual
            url_name: Nombre de la URL de creación
            
        Returns:
            Dict: {day_name: url_creacion}
        """
        create_urls = {}
        
        days_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for i, day in enumerate(week_range.days):
            day_name = days_names[i]
            create_urls[day_name] = reverse(url_name) + f"?fecha={day.isoformat()}"
        
        return create_urls
