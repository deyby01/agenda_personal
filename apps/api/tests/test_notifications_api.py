from django.urls import reverse
from rest_framework import status

from apps.api.tests.base import BaseAPITestCase
from apps.notifications.models import Notification


class NotificationAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.notification = Notification.objects.create(
            usuario=self.user,
            titulo="Recordatorio",
            mensaje="Mensaje",
            tipo="task",
            subtipo="info",
        )

    def test_mark_notification_as_read(self):
        url = reverse("api:v1:notifications-mark-read", args=[self.notification.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["leida"])

    def test_mark_all_read(self):
        Notification.objects.create(
            usuario=self.user,
            titulo="Recordatorio 2",
            mensaje="Mensaje",
            tipo="system",
            subtipo="warning",
        )
        url = reverse("api:v1:notifications-mark-all-read")
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["updated"], 2)

    def test_unread_count_endpoint(self):
        url = reverse("api:v1:notifications-unread-count")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["unread"], 1)


