"""
Task Services - Business Logic Layer.

Migrated from tareas/services.py
Contains: WeekCalculatorService, WeekNavigationService
"""

import datetime
from typing import Dict, List, Optional, Tuple
from django.utils import timezone
from django.urls import reverse

from apps.core.utils import WeekRange

class WeekCalculatorService:
    """
    Service for week-related calculations.
    
    Single Responsibility: Date and week range calculations.
    """

    @staticmethod
    def get_week_range(year: Optional[int] = None, week: Optional[int] = None) -> WeekRange:
        """
        Gets the week range (Monday to Sunday).

        Args:
            year: Year (default: current year)
            week: Week number (default: current week)

        Returns:
            WeekRange: Object with start_date and end_date
        """

        if year is None or week is None:
            today = timezone.localdate()
            year = today.year
            week = today.isocalendar()[1]

        # Calculate Monday of the week
        jan_4 = datetime.date(year, 1, 4)
        week_1_monday = jan_4 - datetime.timedelta(days=jan_4.weekday())
        monday = week_1_monday + datetime.timedelta(weeks=week - 1)

        # Calculate Sunday
        sunday = monday + datetime.timedelta(days=6)

        return WeekRange(start_date=monday, end_date=sunday)


    @staticmethod
    def get_navigation_weeks(current_week: WeekRange) -> Dict[str, WeekRange]:
        """
        Gets previous and next weeks

        Args:
            current_week (WeekRange): current week

        Returns:
            Dict with 'prev' and 'next' WeekRange
        """
        # Previous week
        prev_monday = current_week.start_date - datetime.timedelta(days=7)
        prev_sunday = prev_monday + datetime.timedelta(days=6)

        # Next week
        next_monday = current_week.start_date + datetime.timedelta(days=7)
        next_sunday = next_monday + datetime.timedelta(days=6)

        return {
            'prev': WeekRange(start_date=prev_monday, end_date=prev_sunday),
            'next': WeekRange(start_date=next_monday, end_date=next_sunday)
        }


    @staticmethod
    def parse_date_params(year_param: Optional[str], week_param: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
        """
        Parses year and week parameters from URL.

        Args:
            year_param (Optional[str]): Year as string
            week_param (Optional[str]): Week as string

        Returns:
            Tuple (year, week) or (None, None) if invalid
        """
        try:
            year = int(year_param) if year_param else None
            week = int(week_param) if week_param else None
            return year, week
        except (ValueError, TypeError):
            return None, None


class WeekNavigationService:
    """
    Service for generating week navigation URLs.
    
    Single Responsibility: Navigation URL generation.
    """

    @staticmethod
    def get_navigation_urls(week_range: WeekRange, url_name: str = 'mi_semana_url') -> Dict[str, str]:
        """
        Generates navigation URLs (prev/next week).

        Args:
            week_range (WeekRange): current week
            url_name (str, optional): Django URL name

        Returns:
            Dict with 'prev_url' and 'next_url'
        """

        nav_weeks = WeekCalculatorService.get_navigation_weeks(week_range)

        prev_week = nav_weeks['prev']
        next_week = nav_weeks['next']

        # Get ISO year and week number
        prev_year, prev_week_num = prev_week.start_date.isocalendar()[:2]
        next_year, next_week_num = next_week.start_date.isocalendar()[:2]

        return {
            'prev_url': reverse(url_name, kwargs={
                'year': prev_year,
                'week': prev_week_num
            }),
            'next_url': reverse(url_name, kwargs={
                'year': next_year,
                'week': next_week_num
            })
        }


    @staticmethod
    def get_create_task_urls(week_range: WeekRange, url_name: str = 'crear_tarea_url') -> Dict[datetime.date, str]:
        """
        Generates URLs to create tasks for each day of the week.

        Args:
            week_range (WeekRange): Current week
            url_name (str, optional): Creation URL name

        Returns:
            Dict: {date: creation_url}
        """

        create_urls = {}

        for day in week_range.days:
            create_urls[day] = reverse(url_name) + f"?fecha={day.isoformat()}"

        return create_urls