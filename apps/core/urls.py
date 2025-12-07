"""
Core URLs - Shared endpoints  
"""

from django.urls import path
from . import views
from apps.tasks.views import DashboardView

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('about-me/', views.AboutMeView.as_view(), name='about_me'),
]