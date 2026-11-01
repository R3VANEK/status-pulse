from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from accounts.infrastructure.models import User as UserModel

URL = "/api/auth/login"
PASSWORD = "Very-Strong-Pass-1"


class LoginEndpointTests(APITestCase):
    def setUp(self) -> None:
        self.user = UserModel.objects.create_user(
            email="jan@example.com", password=PASSWORD
        )

    def test_returns_token_pair_for_valid_credentials(self) -> None:
        response = self.client.post(
            URL, {"email": "jan@example.com", "password": PASSWORD}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            str(AccessToken(response.data["access"])["user_id"]), str(self.user.pk)
        )

    def test_email_is_case_insensitive(self) -> None:
        response = self.client.post(
            URL, {"email": "JAN@Example.com", "password": PASSWORD}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rejects_wrong_password(self) -> None:
        response = self.client.post(
            URL,
            {"email": "jan@example.com", "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rejects_unknown_email_with_the_same_message(self) -> None:
        wrong_password = self.client.post(
            URL,
            {"email": "jan@example.com", "password": "wrong-password"},
            format="json",
        )
        unknown_email = self.client.post(
            URL, {"email": "nobody@example.com", "password": PASSWORD}, format="json"
        )

        self.assertEqual(unknown_email.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(unknown_email.data, wrong_password.data)

    def test_rejects_inactive_user(self) -> None:
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            URL, {"email": "jan@example.com", "password": PASSWORD}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
