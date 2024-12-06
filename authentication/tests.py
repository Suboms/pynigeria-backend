from rest_framework.test import APITransactionTestCase
from .models import User
from django.urls import reverse


class RegisterTestCase(APITransactionTestCase):
    def setUp(self):
        self.register_path = reverse("authentication:register")
        User.objects.create_user(email="test@gmail.com")

    def test_register_success(self):
        response = self.client.post(
            self.register_path, data={"email": "test1@gmail.com"}
        )
        for field in {"id", "email", "message"}:
            self.assertTrue(field in response.data["data"])
        self.assertEqual(response.data["data"]["is_email_verified"], False)

        user = User.objects.filter(email="test1@gmail.com").first()
        self.assertTrue(user.is_otp_email_sent)

    def test_register_integrity_failure(self):
        response = self.client.post(
            self.register_path, data={"email": "test@gmail.com"}
        )
        self.assertEqual(
            response.data["detail"], "An account with this email already exists."
        )

    def test_register_throttled(self):
        for i in range(14):
            response = self.client.post(
                self.register_path, data={"email": f"test{i}@gmail.com"}
            )
        self.assertEqual(
            response.data["detail"],
            "Request was throttled. Expected available in 60 seconds.",
        )
