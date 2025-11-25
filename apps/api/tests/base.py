from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class BaseAPITestCase(APITestCase):
    """
    Configuración base compartida por todos los módulos de prueba.
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username="tester", password="pass123")
        self.other_user = User.objects.create_user(username="other", password="pass123")
        self.client.force_authenticate(self.user)


