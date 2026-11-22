import logging
from typing import Any

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.application.interfaces import TokenPair
from accounts.application.use_cases import (
    log_in_user,
    refresh_tokens,
    register_user,
)
from accounts.infrastructure.password_policy import DjangoPasswordPolicy
from accounts.infrastructure.repositories import DjangoUserRepository
from accounts.infrastructure.token_service import SimpleJwtTokenService
from accounts.presentation.serializers import (
    CredentialsSerializer,
    RefreshSerializer,
    TokenPairSerializer,
)

logger = logging.getLogger(__name__)

INVALID_REQUEST_DETAILS = "Invalid request data."
UNEXPECTED_ERROR_DETAILS = "Something went wrong. Please try again later."


def _tokens_response(tokens: TokenPair, status_code: int) -> Response:
    return Response(TokenPairSerializer(tokens).data, status=status_code)


def _error_response(
    details: str, status_code: int, errors: dict[str, Any] | None = None
) -> Response:
    """Every error response has "details"; field errors go to "errors"."""
    body: dict[str, Any] = {"details": details}
    if errors:
        body["errors"] = errors
    return Response(body, status=status_code)


def _unexpected_error_response() -> Response:
    # Called inside an "except" block, so the full traceback lands in the logs.
    logger.exception("Unexpected error in accounts API")
    return _error_response(
        UNEXPECTED_ERROR_DETAILS, status.HTTP_500_INTERNAL_SERVER_ERROR
    )


class PublicAPIView(APIView):
    """Base view for endpoints used without a valid access token."""

    authentication_classes = ()
    permission_classes = (AllowAny,)


class RegistrationView(PublicAPIView):
    def post(self, request: Request) -> Response:
        serializer = CredentialsSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"details": serializer.error_messages},
            )

        use_case = register_user.UseCase(
            users=DjangoUserRepository(),
            password_policy=DjangoPasswordPolicy(),
            tokens=SimpleJwtTokenService(),
        )
        command = register_user.Command(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        tokens = use_case.execute(command)

        return Response(
            TokenPairSerializer(tokens).data, status=status.HTTP_201_CREATED
        )


class LoginView(PublicAPIView):
    def post(self, request: Request) -> Response:

        serializer = CredentialsSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"details": serializer.error_messages},
            )

        use_case = log_in_user.UseCase(
            users=DjangoUserRepository(), tokens=SimpleJwtTokenService()
        )
        command = log_in_user.Command(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        tokens = use_case.execute(command)

        return Response(TokenPairSerializer(tokens).data, status=status.HTTP_200_OK)


class RefreshView(PublicAPIView):
    def post(self, request: Request) -> Response:

        serializer = RefreshSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"details": serializer.error_messages},
            )

        use_case = refresh_tokens.UseCase(tokens=SimpleJwtTokenService())
        command = refresh_tokens.Command(
            refresh_token=serializer.validated_data["refresh"]
        )

        tokens = use_case.execute(command)

        return Response(TokenPairSerializer(tokens).data, status=status.HTTP_200_OK)
