from django.urls import include, path


app_name = "v1"

urlpatterns = [
    path("", include("apps.api.v1.tasks.urls")),
    path("", include("apps.api.v1.projects.urls")),
    path("", include("apps.api.v1.notifications.urls")),
]


