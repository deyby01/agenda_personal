"""
Utility functions layer - Reusable helper functions

Este módulo contiene funciones de utilidad puras que se usan
en múltiples partes de la aplicación, siguiendo DRY principles.

Características:
- Funciones puras (mismo input → mismo output)
- Sin dependencias de Django específicas
- Fácilmente testeable
- Reutilizable en cualquier parte del código
"""

import datetime
import re
import unicodedata
import decimal
from typing import List, Dict, Any, Optional, Union
from decimal import Decimal


class DateFormatters:
    """
    Utilidades para formateo consistente de fechas en la aplicación.
    
    Centraliza todos los formatos de fecha para mantener consistencia
    visual en toda la aplicación.
    """
    
    # Date format constants
    DISPLAY_FORMAT = "%d %b %Y"           # "15 Oct 2025"
    INPUT_FORMAT = "%Y-%m-%d"             # "2025-10-15"
    DATETIME_FORMAT = "%d %b %Y %H:%M"    # "15 Oct 2025 14:30"
    SHORT_FORMAT = "%d/%m/%y"             # "15/10/25"
    ISO_FORMAT = "%Y-%m-%d"               # "2025-10-15"
    
    # Month names in Spanish
    MONTHS_ES = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
    }
    
    @classmethod
    def format_display_date(cls, date: datetime.date) -> str:
        """
        Formatea fecha para mostrar al usuario.
        
        Args:
            date: Fecha a formatear
            
        Returns:
            Fecha formateada como "15 Oct 2025"
        """
        if not date:
            return ""
        
        day = date.day
        month = cls.MONTHS_ES[date.month]
        year = date.year
        
        return f"{day} {month} {year}"
    
    @classmethod
    def format_relative_date(cls, date: datetime.date, today: Optional[datetime.date] = None) -> str:
        """
        Formatea fecha de manera relativa (hoy, ayer, mañana, etc.).
        
        Args:
            date: Fecha a formatear
            today: Fecha actual (opcional, usa datetime.date.today() si no se proporciona)
            
        Returns:
            Fecha relativa como "Hoy", "Ayer", "Mañana", o fecha formateada
        """
        if not date:
            return ""
        
        if today is None:
            today = datetime.date.today()
        
        days_diff = (date - today).days
        
        if days_diff == 0:
            return "Hoy"
        elif days_diff == 1:
            return "Mañana"
        elif days_diff == -1:
            return "Ayer"
        elif days_diff == 2:
            return "Pasado mañana"
        elif days_diff == -2:
            return "Anteayer"
        elif 0 < days_diff <= 7:
            weekdays = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
            return weekdays[date.weekday()]
        else:
            return cls.format_display_date(date)
    
    @classmethod
    def format_datetime_display(cls, dt: datetime.datetime) -> str:
        """
        Formatea datetime para mostrar al usuario.
        
        Args:
            dt: DateTime a formatear
            
        Returns:
            DateTime formateado como "15 Oct 2025 14:30"
        """
        if not dt:
            return ""
        
        date_part = cls.format_display_date(dt.date())
        time_part = dt.strftime("%H:%M")
        
        return f"{date_part} {time_part}"
    
    @classmethod
    def parse_date_string(cls, date_string: str) -> Optional[datetime.date]:
        """
        Parsea string de fecha en varios formatos comunes.
        
        Args:
            date_string: String de fecha a parsear
            
        Returns:
            datetime.date si es válido, None si no se puede parsear
        """
        if not date_string:
            return None
        
        # Formatos a intentar
        formats = [
            "%Y-%m-%d",    # 2025-10-15
            "%d/%m/%Y",    # 15/10/2025
            "%d-%m-%Y",    # 15-10-2025
            "%d/%m/%y",    # 15/10/25
        ]
        
        for format_str in formats:
            try:
                return datetime.datetime.strptime(date_string, format_str).date()
            except ValueError:
                continue
        
        return None


class StringValidators:
    """
    Utilidades para validación de strings y datos de entrada.
    
    Funciones puras para validar diferentes tipos de datos
    sin dependencias externas.
    """
    
    # Regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?[\d\s\-\(\)]{7,15}$')
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Valida si un email tiene formato válido.
        
        Args:
            email: String de email a validar
            
        Returns:
            True si es válido, False en caso contrario
        """
        if not email or not isinstance(email, str):
            return False
        
        return bool(StringValidators.EMAIL_PATTERN.match(email.strip()))
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """
        Valida si un teléfono tiene formato válido.
        
        Args:
            phone: String de teléfono a validar
            
        Returns:
            True si es válido, False en caso contrario
        """
        if not phone or not isinstance(phone, str):
            return False
        
        return bool(StringValidators.PHONE_PATTERN.match(phone.strip()))
    
    @staticmethod
    def clean_text(text: str, max_length: Optional[int] = None) -> str:
        """
        Limpia un texto removiendo espacios extra y caracteres no deseados.
        
        Args:
            text: Texto a limpiar
            max_length: Longitud máxima (opcional)
            
        Returns:
            Texto limpio
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Remover espacios extra
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Truncar si es necesario
        if max_length and len(cleaned) > max_length:
            cleaned = cleaned[:max_length].rsplit(' ', 1)[0] + '...'
        
        return cleaned
    
    @staticmethod
    def slugify(text: str) -> str:
        """
        Convierte texto a slug válido para URLs.
        
        Args:
            text: Texto a convertir
            
        Returns:
            Slug válido para URLs
        """
        if not text:
            return ""
        
        # Normalizar unicode
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        # Convertir a minúsculas y reemplazar espacios
        text = re.sub(r'[^\w\s-]', '', text.lower())
        text = re.sub(r'[-\s]+', '-', text)
        
        return text.strip('-')


class DataConverters:
    """
    Utilidades para conversión de datos entre diferentes formatos.
    
    Funciones para transformar datos de manera consistente
    en toda la aplicación.
    """
    
    @staticmethod
    def dict_to_query_params(data: Dict[str, Any]) -> str:
        """
        Convierte diccionario a query parameters para URLs.
        
        Args:
            data: Diccionario con datos
            
        Returns:
            String con query parameters
        """
        if not data:
            return ""
        
        params = []
        for key, value in data.items():
            if value is not None:
                params.append(f"{key}={value}")
        
        return "&".join(params)
    
    @staticmethod
    def safe_decimal(value: Union[str, int, float]) -> Optional[Decimal]:
        if value is None:
            return None
        
        try:
            return Decimal(str(value))
        except (ValueError, TypeError, decimal.InvalidOperation):  # ← FIXED
            return None
    
    @staticmethod
    def safe_int(value: Union[str, int, float]) -> Optional[int]:
        """
        Convierte valor a int de manera segura.
        
        Args:
            value: Valor a convertir
            
        Returns:
            int si es válido, None en caso contrario
        """
        if value is None:
            return None
        
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
        """
        Trunca texto a longitud máxima con sufijo.
        
        Args:
            text: Texto a truncar
            max_length: Longitud máxima
            suffix: Sufijo a agregar si se trunca
            
        Returns:
            Texto truncado
        """
        if not text or len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix


class PerformanceHelpers:
    """
    Utilidades para optimización y medición de performance.
    
    Funciones para mejorar performance y debugging.
    """
    
    @staticmethod
    def batch_items(items: List[Any], batch_size: int = 100) -> List[List[Any]]:
        """
        Divide lista en batches para procesamiento eficiente.
        
        Args:
            items: Lista de items
            batch_size: Tamaño de cada batch
            
        Returns:
            Lista de batches
        """
        if not items:
            return []
        
        return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    
    @staticmethod
    def deduplicate_list(items: List[Any], key_func: Optional[callable] = None) -> List[Any]:
        """
        Remueve duplicados de lista manteniendo orden.
        
        Args:
            items: Lista con posibles duplicados
            key_func: Función para extraer key de comparación (opcional)
            
        Returns:
            Lista sin duplicados
        """
        if not items:
            return []
        
        seen = set()
        result = []
        
        for item in items:
            key = key_func(item) if key_func else item
            
            if key not in seen:
                seen.add(key)
                result.append(item)
        
        return result
