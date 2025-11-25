from django.urls import reverse
from rest_framework import status

from apps.api.tests.base import BaseAPITestCase
from apps.projects.models import Proyecto
from apps.tasks.models import Tarea


class TaskAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.project = Proyecto.objects.create(
            usuario=self.user,
            nombre="Proyecto API",
            descripcion="API",
            estado="planificado",
        )
        self.task = Tarea.objects.create(
            usuario=self.user,
            titulo="Tarea 1",
            descripcion="desc",
            proyecto=self.project,
        )
        Tarea.objects.create(
            usuario=self.other_user,
            titulo="Tarea ajena",
        )

    def test_list_tasks_returns_only_user_data(self):
        url = reverse("api:v1:tasks-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["titulo"], "Tarea 1")

    def test_create_task_sets_owner(self):
        url = reverse("api:v1:tasks-list")
        payload = {"titulo": "Nueva tarea", "descripcion": "test"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["usuario"], self.user.id)

    def test_mark_complete_action(self):
        url = reverse("api:v1:tasks-mark-complete", args=[self.task.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["completada"])


