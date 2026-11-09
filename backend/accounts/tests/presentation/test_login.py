from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from accounts.domain.exceptions import InvalidCredentialsException
from accounts.infrastructure.models import User as UserModel

URL = "/api/auth/login"
PAYLOAD = {"email": "jan@example.com", "password": "Very-Strong-Pass-1"}
USE_CASE = "accounts.presentation.views.LoginUserUseCase.execute"


class LoginEndpointTests(APITestCase):
    def test_returns_token_pair_for_valid_credentials(self) -> None:
        user = UserModel.objects.create_user(
            email=PAYLOAD["email"], password=PAYLOAD["password"]
        )

        response = self.client.post(URL, PAYLOAD, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), {"access", "refresh"})
        access = AccessToken(response.data["access"])
        self.assertEqual(str(access["user_id"]), str(user.pk))

    def test_error_mapping(self) -> None:
        with self.subTest(error="InvalidCredentialsException"):
            with patch(USE_CASE, side_effect=InvalidCredentialsException()):
                response = self.client.post(URL, PAYLOAD, format="json")

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertEqual(response.data, {"details": "Invalid email or password."})

        with self.subTest(error="unexpected"):
            with patch(USE_CASE, side_effect=RuntimeError("database exploded")):
                with self.assertLogs("accounts.presentation.views", level="ERROR"):
                    response = self.client.post(URL, PAYLOAD, format="json")

            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            self.assertIn("details", response.data)
            self.assertNotIn("database exploded", response.data["details"])

        with self.subTest(error="invalid payload"):
            response = self.client.post(URL, {}, format="json")

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("details", response.data)
            self.assertEqual(set(response.data["errors"]), {"email", "password"})
