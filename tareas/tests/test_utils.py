"""
Tests for utility functions
"""
import datetime
from decimal import Decimal
from django.test import TestCase

from tareas.utils import DateFormatters, StringValidators, DataConverters, PerformanceHelpers


class DateFormattersTest(TestCase):
    """Test date formatting utilities"""
    
    def setUp(self):
        self.test_date = datetime.date(2025, 10, 15)
        self.test_datetime = datetime.datetime(2025, 10, 15, 14, 30, 0)
    
    def test_format_display_date(self):
        """format_display_date debe formatear fecha correctamente"""
        result = DateFormatters.format_display_date(self.test_date)
        self.assertEqual(result, "15 Oct 2025")
    
    def test_format_display_date_empty(self):
        """format_display_date debe manejar fecha vacía"""
        result = DateFormatters.format_display_date(None)
        self.assertEqual(result, "")
    
    def test_format_relative_date_today(self):
        """format_relative_date debe detectar 'hoy' correctamente"""
        today = datetime.date(2025, 10, 15)
        result = DateFormatters.format_relative_date(self.test_date, today)
        self.assertEqual(result, "Hoy")
    
    def test_format_relative_date_yesterday(self):
        """format_relative_date debe detectar 'ayer' correctamente"""
        today = datetime.date(2025, 10, 16)
        result = DateFormatters.format_relative_date(self.test_date, today)
        self.assertEqual(result, "Ayer")
    
    def test_format_relative_date_tomorrow(self):
        """format_relative_date debe detectar 'mañana' correctamente"""
        today = datetime.date(2025, 10, 14)
        result = DateFormatters.format_relative_date(self.test_date, today)
        self.assertEqual(result, "Mañana")
    
    def test_parse_date_string_iso_format(self):
        """parse_date_string debe parsear formato ISO"""
        result = DateFormatters.parse_date_string("2025-10-15")
        self.assertEqual(result, self.test_date)
    
    def test_parse_date_string_invalid(self):
        """parse_date_string debe devolver None para formato inválido"""
        result = DateFormatters.parse_date_string("invalid-date")
        self.assertIsNone(result)


class StringValidatorsTest(TestCase):
    """Test string validation utilities"""
    
    def test_is_valid_email_valid(self):
        """is_valid_email debe validar emails correctos"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@domain.com"
        ]
        
        for email in valid_emails:
            with self.subTest(email=email):
                self.assertTrue(StringValidators.is_valid_email(email))
    
    def test_is_valid_email_invalid(self):
        """is_valid_email debe rechazar emails incorrectos"""
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "test@",
            "",
            None
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                self.assertFalse(StringValidators.is_valid_email(email))
    
    def test_clean_text_removes_extra_spaces(self):
        """clean_text debe remover espacios extra"""
        text = "  Texto   con    espacios   extra  "
        result = StringValidators.clean_text(text)
        self.assertEqual(result, "Texto con espacios extra")
    
    def test_slugify_converts_to_slug(self):
        """slugify debe convertir texto a slug válido"""
        text = "Mi Título con Espacios & Símbolos!"
        result = StringValidators.slugify(text)
        self.assertEqual(result, "mi-titulo-con-espacios-simbolos")


class DataConvertersTest(TestCase):
    """Test data conversion utilities"""
    
    def test_dict_to_query_params(self):
        """dict_to_query_params debe convertir dict a query string"""
        data = {"param1": "value1", "param2": "value2"}
        result = DataConverters.dict_to_query_params(data)
        
        # Puede estar en cualquier orden
        self.assertIn("param1=value1", result)
        self.assertIn("param2=value2", result)
        self.assertIn("&", result)
    
    def test_safe_decimal_valid(self):
        """safe_decimal debe convertir valores válidos"""
        test_cases = [
            ("123.45", Decimal("123.45")),
            (123, Decimal("123")),
            (123.45, Decimal("123.45"))
        ]
        
        for input_val, expected in test_cases:
            with self.subTest(input_val=input_val):
                result = DataConverters.safe_decimal(input_val)
                self.assertEqual(result, expected)
    
    def test_safe_decimal_invalid(self):
        """safe_decimal debe devolver None para valores inválidos"""
        invalid_values = ["invalid", None, ""]
        
        for value in invalid_values:
            with self.subTest(value=value):
                result = DataConverters.safe_decimal(value)
                self.assertIsNone(result)
    
    def test_truncate_text(self):
        """truncate_text debe truncar texto correctamente"""
        text = "Este es un texto muy largo que necesita ser truncado"
        result = DataConverters.truncate_text(text, 20)
        
        self.assertTrue(len(result) <= 20)
        self.assertTrue(result.endswith("..."))


class PerformanceHelpersTest(TestCase):
    """Test performance helper utilities"""
    
    def test_batch_items(self):
        """batch_items debe dividir lista en batches"""
        items = list(range(25))  # [0, 1, 2, ..., 24]
        batches = PerformanceHelpers.batch_items(items, batch_size=10)
        
        self.assertEqual(len(batches), 3)  # 3 batches
        self.assertEqual(len(batches[0]), 10)  # First batch: 10 items
        self.assertEqual(len(batches[1]), 10)  # Second batch: 10 items  
        self.assertEqual(len(batches[2]), 5)   # Third batch: 5 items
    
    def test_deduplicate_list(self):
        """deduplicate_list debe remover duplicados manteniendo orden"""
        items = [1, 2, 3, 2, 4, 1, 5]
        result = PerformanceHelpers.deduplicate_list(items)
        
        expected = [1, 2, 3, 4, 5]
        self.assertEqual(result, expected)
    
    def test_deduplicate_list_with_key_func(self):
        """deduplicate_list debe usar key_func para comparación"""
        items = [
            {"id": 1, "name": "A"},
            {"id": 2, "name": "B"},
            {"id": 1, "name": "A"},  # Duplicate
            {"id": 3, "name": "C"}
        ]
        
        result = PerformanceHelpers.deduplicate_list(items, key_func=lambda x: x["id"])
        
        self.assertEqual(len(result), 3)
        ids = [item["id"] for item in result]
        self.assertEqual(ids, [1, 2, 3])
