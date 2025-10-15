"""
Test for dashboard functionality
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse
import datetime
from django.utils import timezone

# Business logic
from tareas.models import Tarea, Proyecto
from tareas.business_logic import TaskPrioritizationEngine, ProjectProgressCalculator

class DashboardViewTest(TestCase):
    """ Test intelligent dashboard """

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )

        self.client = Client()

    def test_dashboard_url_exists_without_login(self):
        """
        Test that dashboard URL exists and is accessible without login
        """

        # Try to access dashboard without login
        url = reverse('dashboard')
        response = self.client.get(url)

        # Redirect code (302)
        self.assertEqual(response.status_code, 302)

        # Redirect to login page
        self.assertIn('/accounts/login/', response.url)

    def test_dashboard_url_exists_with_login(self):
        """
        Test that dashboard URL loads succesfully for autheticated user
        """
        # Login
        self.client.login(username='testuser', password='testpassword')

        # Access dashboard
        url = reverse('dashboard')
        response = self.client.get(url)

        # Should load successfully
        self.assertEqual(response.status_code, 200)

        # Should show dashboard content
        self.assertContains(response, 'Dashboard Inteligente')
        self.assertContains(response, self.user.username)


    def test_dashboard_shows_user_tasks_prioritized(self):
        """
        Dashboard should show user's tasks organized by priority zones
        - Critical zone: Overdue + due today tasks
        - Attention Zone: this week + next weeks tasks
        - Future Zone: tasks with plenty of time

        Uses TaskPrioritizationEngine for intelligent sorting
        """
        # Login user
        self.client.login(username='testuser', password='testpassword')

        # Tasks with different urgency levels.
        today = timezone.now().date()

        # CRITICAL ZONE: Overdue task
        overdue_task = Tarea.objects.create(
            titulo='Overdue Task',
            descripcion='This should appear in critical zone',
            fecha_asignada=today - datetime.timedelta(days=2), # 2 days ago
            usuario=self.user
        )

        # CRITICAL ZON: Due today
        today_task = Tarea.objects.create(
            titulo='Due Today Task',
            descripcion='This should appear in critical zone',
            fecha_asignada=today,
            usuario=self.user
        )

        # ATTENTION ZONE: Due this week
        this_week_task = Tarea.objects.create(
            titulo='This Week Task',
            descripcion='This should appear in attention zone',
            fecha_asignada=today + datetime.timedelta(days=3), # 3 days from now
            usuario=self.user
        )

        # ATTENTION ZONE: Due next week
        next_week_task = Tarea.objects.create(
            titulo='Next Week Task',
            descripcion='This should appear in attention zone',
            fecha_asignada=today + datetime.timedelta(days=10), # 10 days from now
            usuario=self.user
        )

        # FUTURE ZONE: Plenty of time
        future_task = Tarea.objects.create(
            titulo='Future Task',
            descripcion='This should appear in future zone',
            fecha_asignada=today + datetime.timedelta(days=30), # 30 days from now
            usuario=self.user
        )

        # Get user's tasks
        tasks = Tarea.objects.filter(usuario=self.user)

        # Access dashboard
        url = reverse('dashboard')
        response = self.client.get(url)

        # Basic checks: Should show all user's tasks
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Overdue Task')
        self.assertContains(response, 'Due Today Task')
        self.assertContains(response, 'This Week Task')
        self.assertContains(response, 'Next Week Task')
        self.assertContains(response, 'Future Task')

        # Advanced checks: Should organized by priority zones
        self.assertContains(response, 'Critical') # Critical zone section
        self.assertContains(response, 'Attention') # Attention zone section
        self.assertContains(response, 'Future') # Future zone section