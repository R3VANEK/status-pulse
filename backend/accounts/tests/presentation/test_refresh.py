from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from accounts.domain.exceptions import InvalidTokenException
from accounts.infrastructure.models import User as UserModel

REGISTRATION_URL = "/api/auth/registration"
URL = "/api/auth/refresh"
USE_CASE = "accounts.presentation.views.RefreshTokensUseCase.execute"


class RefreshEndpointTests(APITestCase):
    def test_returns_new_token_pair(self) -> None:
        # Real flow: register, then refresh what the registration returned.
        registration = self.client.post(
            REGISTRATION_URL,
            {"email": "jan@example.com", "password": "Very-Strong-Pass-1"},
            format="json",
        )
        user = UserModel.objects.get(email="jan@example.com")
        old_refresh = registration.data["refresh"]
        # The frontend may still send its expired access token – it must not matter.
        expired_access = AccessToken.for_user(user)
        expired_access.set_exp(from_time=timezone.now() - timedelta(hours=1))

        response = self.client.post(
            URL,
            {"refresh": old_refresh},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {expired_access}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), {"access", "refresh"})
        self.assertNotEqual(response.data["refresh"], old_refresh)
        access = AccessToken(response.data["access"])
        self.assertEqual(str(access["user_id"]), str(user.pk))

        # Rotation: the used refresh token is blacklisted and cannot be reused.
        reused = self.client.post(URL, {"refresh": old_refresh}, format="json")
        self.assertEqual(reused.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_error_mapping(self) -> None:
        payload = {"refresh": "any-token"}

        with self.subTest(error="InvalidTokenException"):
            with patch(USE_CASE, side_effect=InvalidTokenException()):
                response = self.client.post(URL, payload, format="json")

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertEqual(response.data, {"details": "Token is invalid or expired."})

        with self.subTest(error="unexpected"):
            with patch(USE_CASE, side_effect=RuntimeError("database exploded")):
                with self.assertLogs("accounts.presentation.views", level="ERROR"):
                    response = self.client.post(URL, payload, format="json")

            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            self.assertIn("details", response.data)
            self.assertNotIn("database exploded", response.data["details"])

        with self.subTest(error="invalid payload"):
            response = self.client.post(URL, {}, format="json")

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("details", response.data)
            self.assertIn("refresh", response.data["errors"])
