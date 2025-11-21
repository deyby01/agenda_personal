"""
Utilidades compartidas entre módulos.

Contiene:
- Value Objects (WeekRange)
- Helper functions
- Common validators
"""

import datetime
from typing import List, NamedTuple

class WeekRange(NamedTuple):
    """
    Value Object que representa un rango de semana.
    
    Inmutable (NamedTuple) siguiendo DDD principles.
    
    Attributes:
        start_date: Fecha de inicio (lunes)
        end_date: Fecha de fin (domingo)
    
    Example:
        >>> week = WeekRange(
        ...     start_date=datetime.date(2025, 11, 11),
        ...     end_date=datetime.date(2025, 11, 17)
        ... )
        >>> week.days  # Lista de 7 días
        >>> week.is_current_week  # bool
    """

    start_date: datetime.date
    end_date: datetime.date

    @property
    def days(self) -> List[datetime.date]:
        """
        Obtiene lista de los 7 dias de la semana.

        Returns:
            List[datetime.date]: Lista ordenada de fechas
        """
        return [
            self.start_date + datetime.timedelta(days=i)
            for i in range(7)
        ]
    
    @property
    def is_current_week(self) -> bool:
        """
        Verifica si este rango incluye el dia actual.

        Returns:
            bool: True si hoy esta en este rango
        """
        from django.utils import timezone
        today = timezone.localdate()
        return self.start_date <= today <= self.end_date

    def format_display(self) -> str:
        """
        Formatea el rango para mostrar en UI.

        Returns:
            str: Formato legible (ej: "11 - 17 Nov 2025")
        """
        if self.start_date.month == self.end_date.month:
            return f"{self.start_date.strftime('%d')} - {self.end_date.strftime('%d %b %Y')}"
        return f"{self.start_date.strftime('%d %b')} - {self.end_date.strftime('%d %b %Y')}"
        
    def __str__(self) -> str:
        """ String representation for debugging """
        return f"Week({self.start_date} to {self.end_date})"