from django.test import TestCase
from django.urls import reverse

# Create your tests here.


class TestUserLogin(TestCase):
    def test_post(self):
        response = self.client.post(
            reverse("home"), {"email": "test@example.com", "display_name": "Ian"}
        )

        self.assertRedirects(response, reverse("home"))
        self.assertEqual(response.cookies.get("email"), "test@example.com")
