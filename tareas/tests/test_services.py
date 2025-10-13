"""
Tests for service layer components following SOLID principles
"""
from calendar import week
import datetime
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch

from tareas.services import WeekCalculatorService, WeekNavegationService, WeekRange

class WeekRangeTest(TestCase):
    """ Test WeekRange value object """

    def setUp(self):
        # Lunes 13 octubre 2025
        self.start_date = datetime.date(2025, 10, 13)
        # Domingo 19
        self.end_date = datetime.date(2025, 10, 19)
        self.week_range = WeekRange(self.start_date, self.end_date)

    def test_days_property_returns_seven_days(self):
        """
        WeekRange.days debe devolver 7 dias consecutivos.
        """
        days = self.week_range.days

        self.assertEqual(len(days), 7)
        self.assertEqual(days[0], self.start_date)
        self.assertEqual(days[6], self.end_date)

    def test_is_current_week_property(self):
        """
        WeekRange.is_current_week debe detectar correctamente semana actual.
        """
        today = datetime.date(2025, 10, 15)

        with patch('django.utils.timezone.localdate', return_value=today):
            self.assertTrue(self.week_range.is_current_week)

        # fecha fuera del rango
        other_day = datetime.date(2025, 10, 25)
        with patch('django.utils.timezone.localdate', return_value=other_day):
            self.assertFalse(self.week_range.is_current_week)

    def test_format_display_different_months(self):
        """
        format_display debe formatear fechas de meses diferentes.
        """
        # Semana que cruza meses: 28 Oct - 3 Nov 2025
        week_range = WeekRange(
            datetime.date(2025, 10, 28),
            datetime.date(2025, 11, 3),
        )
        expected = "28 Oct - 03 Nov 2025"
        self.assertEqual(week_range.format_display(), expected)

    

class WeekCalculatorServiceTest(TestCase):
    """ Test WeekCalculatorService business logic """

    def test_get_week_range_with_monday(self):
        """
        get_week_range con lunes debe devolver la misma semana 
        """
        monday = datetime.date(2025, 10, 13)
        week_range = WeekCalculatorService.get_week_range(monday)

        self.assertEqual(week_range.start_date, monday)
        self.assertEqual(week_range.end_date, datetime.date(2025, 10, 19))

    def test_get_week_range_with_friday(self):
        """
        get_week_range con viernes debe devolver lunes de esa semana.
        """
        friday = datetime.date(2025, 10, 17)
        week_range = WeekCalculatorService.get_week_range(friday)

        self.assertEqual(week_range.start_date, datetime.date(2025, 10, 13))
        self.assertEqual(week_range.end_date, datetime.date(2025, 10, 19))

    def test_get_week_range_without_date_uses_today(self):
        """
        get_week_range sin parametros debe usar fecha actual.
        """
        today = datetime.date(2025, 10, 15)
        with patch('django.utils.timezone.localdate', return_value=today):
            week_range = WeekCalculatorService.get_week_range()

            self.assertEqual(week_range.start_date, datetime.date(2025, 10, 13))
            self.assertEqual(week_range.end_date, datetime.date(2025, 10, 19))

    
    def test_get_navigation_weeks(self):
        """
        get_navigation_weeks debe calcular semanas anterior y siguiente.
        """
        current_week = WeekRange(
            datetime.date(2025, 10, 13),
            datetime.date(2025, 10, 19),
        )

        navigation = WeekCalculatorService.get_navigation_weeks(current_week)

        # Semana anterior: 6-12 Oct 2025
        self.assertEqual(navigation['previous'].start_date, datetime.date(2025, 10, 6))
        self.assertEqual(navigation['previous'].end_date, datetime.date(2025, 10, 12))

        # Semana siguiente: 20-26 Oct 2025
        self.assertEqual(navigation['next'].start_date, datetime.date(2025, 10, 20))
        self.assertEqual(navigation['next'].end_date, datetime.date(2025, 10, 26))

    def test_parse_date_params_valid_date(self):
        """
        parse_date_params debe parsear fechas validas.
        """
        result = WeekCalculatorService.parse_date_params(2025, 10, 15)
        expected = datetime.date(2025, 10, 15)
        self.assertEqual(result, expected)

    def test_parse_date_params_invalid_date(self):
        """
        parse_date_params debe usar fecha actual para fechas invalidas.
        """
        today = datetime.date(2025, 10, 13)

        with patch('django.utils.timezone.localdate', return_value=today):
            result = WeekCalculatorService.parse_date_params(2025, 13, 45)
            self.assertEqual(result, today)

    def test_parse_date_params_none_values(self):
        """
        parse_date_params debe usar fecha actual si parametros son None.
        """
        today = datetime.date(2025, 10, 13)

        with patch('django.utils.timezone.localdate', return_value=today):
            result = WeekCalculatorService.parse_date_params(None, None, None)
            self.assertEqual(result, today)



class WeekNavigationServiceTest(TestCase):
    """ Test WeekNavigationService URL generation """

    def setUp(self):
        self.current_week = WeekRange(
            datetime.date(2025, 10, 13),
            datetime.date(2025, 10, 19),
        )
        self.navigation_weeks = {
            'previous': WeekRange(
                datetime.date(2025, 10, 6),
                datetime.date(2025, 10, 12),
            ),
            'next': WeekRange(
                datetime.date(2025, 10, 20),
                datetime.date(2025, 10, 26),
            ),
        }

    @patch('tareas.services.WeekRange.is_current_week', False)
    def test_get_navigation_urls_not_current_week(self):
        """
        get_navigation_urls debe generar todas las URLs si no es semana actual.
        """
        urls = WeekNavegationService.get_navigation_urls(self.current_week, self.navigation_weeks)

        self.assertIsNotNone(urls['previous'])
        self.assertIsNotNone(urls['next'])
        self.assertIsNotNone(urls['current'])
        self.assertIn('/mi-semana/2025/10/6', urls['previous'])
        self.assertIn('/mi-semana/2025/10/20', urls['next'])

    @patch('tareas.services.WeekRange.is_current_week', True)
    def test_get_navigation_urls_current_week(self):
        """
        get_navigation_urls debe devolver previous=None si es semana actual.
        """
        urls = WeekNavegationService.get_navigation_urls(self.current_week, self.navigation_weeks)

        self.assertIsNone(urls['previous'])
        self.assertIsNotNone(urls['next'])
        self.assertIsNotNone(urls['current'])

    def test_get_create_task_urls(self):
        """
        get_create_task_urls debe generar URLs para crear tareas por dia
        """
        urls = WeekNavegationService.get_create_task_urls(self.current_week)

        self.assertEqual(len(urls), 7)
        self.assertIn('monday', urls)
        self.assertIn('sunday', urls)
        self.assertIn('fecha_asignada=2025-10-13', urls['monday'])
        self.assertIn('fecha_asignada=2025-10-19', urls['sunday'])
