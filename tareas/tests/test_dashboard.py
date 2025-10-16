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
        self.assertContains(response, 'critical') # Critical zone section
        self.assertContains(response, 'attention') # Attention zone section
        self.assertContains(response, 'future') # Future zone section


    def test_dashboard_shows_project_health_overview(self):
        """
        Dashboard should show project health using ProjectProgressCalculator
        
        Testing Deyby's vision:
        - Active, paused, completed, cancelled projects  
        - Progress percentage for each project
        - Time remaining calculations
        - Health status indicators (🟢 Healthy, ⚠️ At Risk, 🚨 Critical)
        """
        # Login user
        self.client.login(username='testuser', password='testpassword')
        
        # Create test projects with different health states
        today = timezone.now().date()
        
        # HEALTHY PROJECT - On track
        healthy_project = Proyecto.objects.create(
            usuario=self.user,
            nombre='Healthy Project',
            descripcion='This project is on track',
            fecha_inicio=today - datetime.timedelta(days=10),
            fecha_fin_estimada=today + datetime.timedelta(days=20),  # 30 total days, 10 used
            estado='en_curso'
        )
        
        # AT RISK PROJECT - Tight timeline
        risk_project = Proyecto.objects.create(
            usuario=self.user,
            nombre='At Risk Project', 
            descripcion='This project needs attention',
            fecha_inicio=today - datetime.timedelta(days=25),
            fecha_fin_estimada=today + datetime.timedelta(days=5),   # 30 total days, 25 used
            estado='en_curso'
        )
        
        # OVERDUE PROJECT - Past deadline
        overdue_project = Proyecto.objects.create(
            usuario=self.user,
            nombre='Overdue Project',
            descripcion='This project is overdue',
            fecha_inicio=today - datetime.timedelta(days=40),
            fecha_fin_estimada=today - datetime.timedelta(days=5),  # Past deadline
            estado='en_curso'
        )
        
        # COMPLETED PROJECT - Success story
        completed_project = Proyecto.objects.create(
            usuario=self.user,
            nombre='Completed Project',
            descripcion='Successfully finished',
            fecha_inicio=today - datetime.timedelta(days=30),
            fecha_fin_estimada=today - datetime.timedelta(days=5),
            estado='completado'
        )
        
        # Access dashboard
        url = reverse('dashboard')
        response = self.client.get(url)
        
        # Should show project information
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Healthy Project')
        self.assertContains(response, 'At Risk Project')
        self.assertContains(response, 'Overdue Project')  
        self.assertContains(response, 'Completed Project')
        
        # Should show project health sections  
        self.assertContains(response, 'Proyectos')  # Projects section exists
        self.assertContains(response, 'Salud')     # Health indicators exist
        
        # Should show progress information
        self.assertContains(response, '%')         # Progress percentages
        self.assertContains(response, 'días')      # Time remaining info


    def test_dashboard_accessible_from_navbar(self):
        """
        Dashboard should be accessible via navbar link

        Testing navigation integration:
        - Dashboard link exists in bar
        - Link points to correct URL
        - Link is highlighted when active
        """
        # Login user
        self.client.login(username='testuser', password='testpassword')

        # Get any page with navbar (e.g. tasks list)
        response = self.client.get(reverse('lista_de_tareas_url'))

        # Should contain dashboard link in navbar
        self.assertContains(response, 'href="/agenda/dashboard/"')
        self.assertContains(response, 'Dashboard')

        # Get dashboard page
        dashboard_response = self.client.get(reverse('dashboard'))

        # Dashboard navbar link should be active/highlighted
        self.assertContains(dashboard_response, 'nav-link active')

    def test_homepage_redirects_to_dashboard(self):
        """
        Homepage (/) should redirect to intelligence dashboard for logged users

        Testing user experience:
        - Logged users see dashboard inmediately
        - Dashboard becomes primary entry point
        """
        # Login user
        self.client.login(username='testuser', password='testpassword')

        # Access homepage
        response = self.client.get('/')

        # Should redirect to dashboard (or load dashboard directly)
        if response.status_code == 302:
            # Redirect aproach
            self.assertIn('/dashboard/', response.url)
        else:
            # Direct load approach (status 200)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Dashboard Inteligente')

    def test_homepage_shows_login_for_anonymous_users(self):
        """
        Anonymous users should see login page or landig page
        """
        response = self.client.get('/')

        # Should either redirect to login or show login form
        if response.status_code == 302:
            self.assertIn('/accounts/login/', response.url)
        else:
            # Should show login form o landig page
            self.assertIn(response.status_code, [200, 302])

    def test_dashboard_shows_completed_tasks_section_for_motivation(self):
        """
        Dashboard debe mostrar sección motivacional de tareas completadas
        
        Feature: Gamification - mostrar logros para motivar al usuario
        """
        # Login usuario
        self.client.login(username='testuser', password='testpassword')
        
        today = timezone.now().date()
        
        # Crear tareas completadas hoy
        completed_task1 = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Completada 1',
            fecha_asignada=today,
            completada=True  # Completada
        )
        
        completed_task2 = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Completada 2', 
            fecha_asignada=today,
            completada=True  # Completada
        )
        
        # Crear tarea pendiente (no debe aparecer en sección de completadas)
        pending_task = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Pendiente',
            fecha_asignada=today,
            completada=False  # Pendiente
        )
        
        # Acceder al dashboard
        response = self.client.get(reverse('dashboard'))
        
        # Verificar sección de completadas aparece
        self.assertContains(response, 'Tareas Completadas!')
        self.assertContains(response, 'fas fa-trophy')  # Ícono de logro
        
        # Verificar que muestra las tareas completadas
        self.assertContains(response, 'Tarea Completada 1')
        self.assertContains(response, 'Tarea Completada 2')
        
        # Verificar que NO muestra la tarea pendiente en sección de completadas
        # (La pendiente debería estar en zona crítica, no en completadas)
        completed_section = str(response.content).split('Tareas Completadas!')[1].split('</div>')[0]
        self.assertNotIn('Tarea Pendiente', completed_section)
        
        # Verificar mensaje motivacional  
        self.assertContains(response, '¡Sigue así!')
        self.assertContains(response, 'total')  # Contador total de logros
