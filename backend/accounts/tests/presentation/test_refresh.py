from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from accounts.infrastructure.models import User as UserModel

REGISTRATION_URL = "/api/auth/registration"
URL = "/api/auth/refresh"


class RefreshEndpointTests(APITestCase):
    def setUp(self) -> None:
        # Real flow: register first, then refresh what the registration returned.
        response = self.client.post(
            REGISTRATION_URL,
            {"email": "jan@example.com", "password": "Very-Strong-Pass-1"},
            format="json",
        )
        self.tokens = response.data
        self.user = UserModel.objects.get(email="jan@example.com")

    def refresh(self, token: str, **extra: str):  # type: ignore[no-untyped-def]
        return self.client.post(URL, {"refresh": token}, format="json", **extra)

    def test_returns_new_token_pair(self) -> None:
        response = self.refresh(self.tokens["refresh"])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), {"access", "refresh"})
        self.assertNotEqual(response.data["refresh"], self.tokens["refresh"])
        self.assertEqual(
            str(AccessToken(response.data["access"])["user_id"]), str(self.user.pk)
        )

    def test_used_refresh_token_cannot_be_reused(self) -> None:
        self.refresh(self.tokens["refresh"])

        response = self.refresh(self.tokens["refresh"])

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_new_refresh_token_can_be_used(self) -> None:
        first = self.refresh(self.tokens["refresh"])

        second = self.refresh(first.data["refresh"])

        self.assertEqual(second.status_code, status.HTTP_200_OK)

    def test_rejects_access_token(self) -> None:
        response = self.refresh(self.tokens["access"])

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rejects_expired_token(self) -> None:
        token = RefreshToken.for_user(self.user)
        token.set_exp(from_time=timezone.now() - timedelta(days=30))

        response = self.refresh(str(token))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rejects_garbage(self) -> None:
        response = self.refresh("not-a-jwt")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_requires_refresh_field(self) -> None:
        response = self.client.post(URL, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("refresh", response.data)

    def test_works_with_expired_access_token_in_header(self) -> None:
        expired_access = AccessToken.for_user(self.user)
        expired_access.set_exp(from_time=timezone.now() - timedelta(hours=1))

        response = self.refresh(
            self.tokens["refresh"], HTTP_AUTHORIZATION=f"Bearer {expired_access}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
