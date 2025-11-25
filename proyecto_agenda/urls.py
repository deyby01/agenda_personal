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
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Smart homepage routing
def homepage_redirect(request):
    """
    Intelligence homepage routing
    """
    if request.user.is_authenticated:
        # Logged users -> Dashboard 
        return redirect('/dashboard/')
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
    path('agenda/', include('apps.tasks.urls')),
    path('agenda/', include('apps.projects.urls')),
    path('agenda/', include('apps.notifications.urls')),

    # ========== API URLS ========
    path('api/', include('apps.api.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='api-token-obtain'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path(
        'api/docs/swagger/',
        SpectacularSwaggerView.as_view(url_name='api-schema'),
        name='api-swagger',
    ),
    path(
        'api/docs/redoc/',
        SpectacularRedocView.as_view(url_name='api-schema'),
        name='api-redoc',
    ),
]
