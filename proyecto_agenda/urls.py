"""
URL configuration for proyecto_agenda project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from rest_framework.authtoken import views
from django.views.generic.base import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# Smart homepage routing
def homepage_redirect(request):
    """
    Intelligence homepage routing
    """
    if request.user.is_authenticated:
        # Logged users -> Dashboard 
        return redirect('/agenda/dashboard/')
    else:
        # Anonymous users -> login page
        return redirect('/accounts/login/')


urlpatterns = [
    path('admin/', admin.site.urls),

    # ======== INTELLIGENT HOMEPAGE ROUTING ========
    path('', homepage_redirect, name='homepage'),

    # ========= AUTHENTICATION ========
    path('accounts/', include('allauth.urls')),

    # ========= CORE ENDPOINTS ===========
    path('', include('apps.core.urls')), # 🆕 Health check y shared endpoints

    # =========== APP URLS ========
    path('agenda/', include('tareas.urls')),

    # ========== API URLS ========
    path('api/', include('tareas.api_urls')), 
    path('api-token-auth/', views.obtain_auth_token, name='api-token-auth'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    
]
