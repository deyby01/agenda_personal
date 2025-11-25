from django.urls import reverse
from rest_framework import status

from apps.api.tests.base import BaseAPITestCase
from apps.projects.models import Proyecto
from apps.tasks.models import Tarea


class ProjectAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.project = Proyecto.objects.create(
            usuario=self.user,
            nombre="Proyecto Principal",
            estado="planificado",
        )

    def test_change_status(self):
        url = reverse("api:v1:projects-change-status", args=[self.project.id])
        response = self.client.post(url, {"estado": "en_curso"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["estado"], "en_curso")

    def test_stats_endpoint_returns_structure(self):
        Tarea.objects.create(usuario=self.user, titulo="t1", proyecto=self.project, completada=True)
        Tarea.objects.create(usuario=self.user, titulo="t2", proyecto=self.project, completada=False)

        url = reverse("api:v1:projects-stats", args=[self.project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("project", response.data)
        self.assertIn("stats", response.data)
        self.assertEqual(response.data["stats"]["total_tareas"], 2)


