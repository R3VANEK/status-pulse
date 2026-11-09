from unittest.mock import patch

from allauth.account.models import EmailAddress
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from accounts.domain.exceptions import (
    EmailAlreadyTakenException,
    InvalidEmailException,
    WeakPasswordException,
)
from accounts.infrastructure.models import User as UserModel

URL = "/api/auth/registration"
PAYLOAD = {"email": "Jan@Example.com", "password": "Very-Strong-Pass-1"}
USE_CASE = "accounts.presentation.views.RegisterUserUseCase.execute"


class RegistrationEndpointTests(APITestCase):
    def test_registers_user_and_returns_token_pair(self) -> None:
        response = self.client.post(URL, PAYLOAD, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data), {"access", "refresh"})

        user = UserModel.objects.get(email="jan@example.com")
        self.assertTrue(user.check_password(PAYLOAD["password"]))
        self.assertTrue(
            EmailAddress.objects.filter(user=user, primary=True, verified=True).exists()
        )
        access = AccessToken(response.data["access"])
        refresh = RefreshToken(response.data["refresh"])
        self.assertEqual(str(access["user_id"]), str(user.pk))
        self.assertEqual(str(refresh["user_id"]), str(user.pk))

    def test_error_mapping(self) -> None:
        cases = [
            (InvalidEmailException("not-an-email"), "email"),
            (EmailAlreadyTakenException("jan@example.com"), "email"),
            (WeakPasswordException(["Too short."]), "password"),
        ]
        for error, field in cases:
            with self.subTest(error=type(error).__name__):
                with patch(USE_CASE, side_effect=error):
                    response = self.client.post(URL, PAYLOAD, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("details", response.data)
                self.assertIn(field, response.data["errors"])

        with self.subTest(error="unexpected"):
            with patch(USE_CASE, side_effect=RuntimeError("database exploded")):
                with self.assertLogs("accounts.presentation.views", level="ERROR"):
                    response = self.client.post(URL, PAYLOAD, format="json")

            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            self.assertIn("details", response.data)
            # Internal error messages must not leak to the client.
            self.assertNotIn("database exploded", response.data["details"])

        with self.subTest(error="invalid payload"):
            response = self.client.post(URL, {}, format="json")

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("details", response.data)
            self.assertEqual(set(response.data["errors"]), {"email", "password"})
