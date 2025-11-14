"""
Tests para modelos base Core.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel, UserOwnedModel
import datetime

class TestCoreModels(TestCase):
    """ Test para modelos abstractos de Core. """

    def setUp(self):
        """ setUp se ejecuta antes de cada test """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_core_models_are_importable(self):
        """ Test basico: módulos core se pueden importar. """
        from apps.core import models, utils

        # Verificar que existen las clases
        self.assertTrue(hasattr(models, 'TimeStampedModel'))
        self.assertTrue(hasattr(models, 'UserOwnedModel'))
        self.assertTrue(hasattr(utils, 'WeekRange'))

    def test_week_range_value_object(self):
        """ Test WeekRange functionality """
        from apps.core.utils import WeekRange

        week = WeekRange(
            start_date=datetime.date(2025, 11, 11),
            end_date=datetime.date(2025, 11, 17)
        )

        # Verificar que tiene 7 dias
        self.assertEqual(len(week.days), 7)

        # Verificar primer y ultimo dia
        self.assertEqual(week.days[0], datetime.date(2025, 11, 11))
        self.assertEqual(week.days[6], datetime.date(2025, 11, 17))

        # Verificar format_display 
        formatted = week.format_display()
        self.assertIn('Nov', formatted)
        self.assertIn('2025', formatted)

        # Verificar __str__
        str_repr = str(week)
        self.assertIn('Week', str_repr)
        self.assertIn('2025-11-11', str_repr)