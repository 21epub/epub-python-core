from django.test import TestCase
from django.urls import reverse


class TestK8s(TestCase):
    def test_ping(self):
        url = reverse("ping")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content, b"pong")
