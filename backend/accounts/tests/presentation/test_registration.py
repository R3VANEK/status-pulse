from allauth.account.models import EmailAddress
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from accounts.infrastructure.models import User as UserModel

URL = "/api/auth/registration"
STRONG_PASSWORD = "Very-Strong-Pass-1"


class RegistrationEndpointTests(APITestCase):
    def test_registers_user_and_returns_token_pair(self) -> None:
        response = self.client.post(
            URL,
            {"email": "jan@example.com", "password": STRONG_PASSWORD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data), {"access", "refresh"})

        user = UserModel.objects.get(email="jan@example.com")
        self.assertTrue(user.check_password(STRONG_PASSWORD))
        self.assertNotEqual(user.password, STRONG_PASSWORD)  # stored as a hash

        # Both tokens are valid JWTs signed for the new user.
        self.assertEqual(
            str(AccessToken(response.data["access"])["user_id"]), str(user.pk)
        )
        self.assertEqual(
            str(RefreshToken(response.data["refresh"])["user_id"]), str(user.pk)
        )

    def test_registers_email_in_allauth(self) -> None:
        self.client.post(
            URL,
            {"email": "jan@example.com", "password": STRONG_PASSWORD},
            format="json",
        )

        address = EmailAddress.objects.get(email="jan@example.com")
        self.assertTrue(address.primary)
        self.assertFalse(address.verified)

    def test_normalizes_email(self) -> None:
        response = self.client.post(
            URL,
            {"email": "  Jan@Example.COM ", "password": STRONG_PASSWORD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserModel.objects.filter(email="jan@example.com").exists())

    def test_rejects_email_that_is_already_taken(self) -> None:
        UserModel.objects.create_user(email="jan@example.com", password=STRONG_PASSWORD)

        response = self.client.post(
            URL,
            {"email": "JAN@example.com", "password": STRONG_PASSWORD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(UserModel.objects.count(), 1)

    def test_rejects_invalid_email(self) -> None:
        response = self.client.post(
            URL, {"email": "not-an-email", "password": STRONG_PASSWORD}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_rejects_weak_password_and_creates_no_user(self) -> None:
        response = self.client.post(
            URL, {"email": "jan@example.com", "password": "12345"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertFalse(UserModel.objects.exists())

    def test_requires_email_and_password(self) -> None:
        response = self.client.post(URL, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("password", response.data)

    def test_ignores_invalid_authorization_header(self) -> None:
        response = self.client.post(
            URL,
            {"email": "jan@example.com", "password": STRONG_PASSWORD},
            format="json",
            HTTP_AUTHORIZATION="Bearer some-old-or-broken-token",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
