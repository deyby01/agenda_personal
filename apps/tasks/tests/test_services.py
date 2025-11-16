"""
Tests para Services de Tasks.
"""

from django.test import TestCase
from apps.tasks.services import WeekCalculatorService, WeekNavigationService
from apps.core.utils import WeekRange
from datetime import date


class WeekCalculatorServiceTest(TestCase):
    """Tests para WeekCalculatorService"""
    
    def test_get_week_range_current_week(self):
        """Test: Obtener rango de semana actual"""
        week_range = WeekCalculatorService.get_week_range()
        
        # Verificar que es un WeekRange
        self.assertIsInstance(week_range, WeekRange)
        
        # Verificar que tiene 7 días
        self.assertEqual(len(week_range.days), 7)
        
        # Verificar que start_date es lunes
        self.assertEqual(week_range.start_date.weekday(), 0)  # 0 = lunes
        
        # Verificar que end_date es domingo
        self.assertEqual(week_range.end_date.weekday(), 6)  # 6 = domingo
    
    def test_get_week_range_specific_week(self):
        """Test: Obtener rango de semana específica"""
        # Semana 1 de 2025
        week_range = WeekCalculatorService.get_week_range(year=2025, week=1)
        
        self.assertIsInstance(week_range, WeekRange)
        self.assertEqual(len(week_range.days), 7)
        
        # Primera semana de 2025
        self.assertEqual(week_range.start_date.year, 2024)  # Puede empezar en 2024
        self.assertEqual(week_range.start_date.weekday(), 0)  # Lunes
    
    def test_get_navigation_weeks(self):
        """Test: Obtener semanas prev/next"""
        current = WeekRange(
            start_date=date(2025, 11, 10),  # Lunes
            end_date=date(2025, 11, 16)     # Domingo
        )
        
        nav = WeekCalculatorService.get_navigation_weeks(current)
        
        # Verificar que retorna prev y next
        self.assertIn('prev', nav)
        self.assertIn('next', nav)
        
        # Verificar semana anterior
        prev_week = nav['prev']
        self.assertEqual(prev_week.start_date, date(2025, 11, 3))
        self.assertEqual(prev_week.end_date, date(2025, 11, 9))
        
        # Verificar semana siguiente
        next_week = nav['next']
        self.assertEqual(next_week.start_date, date(2025, 11, 17))
        self.assertEqual(next_week.end_date, date(2025, 11, 23))
    
    def test_parse_date_params_valid(self):
        """Test: Parsear parámetros válidos"""
        year, week = WeekCalculatorService.parse_date_params('2025', '45')
        
        self.assertEqual(year, 2025)
        self.assertEqual(week, 45)
    
    def test_parse_date_params_invalid(self):
        """Test: Parsear parámetros inválidos"""
        year, week = WeekCalculatorService.parse_date_params('invalid', 'bad')
        
        self.assertIsNone(year)
        self.assertIsNone(week)
    
    def test_parse_date_params_none(self):
        """Test: Parsear parámetros None"""
        year, week = WeekCalculatorService.parse_date_params(None, None)
        
        self.assertIsNone(year)
        self.assertIsNone(week)
