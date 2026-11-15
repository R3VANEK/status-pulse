import logging

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.application.interfaces import TokenPair
from accounts.application.use_cases.log_in_user import (
    LoginUserUseCase,
    LoginUserCommand,
)
from accounts.application.use_cases.refresh_tokens import (
    RefreshTokensUseCase,
    RefreshTokensCommand,
)
from accounts.application.use_cases.register_user import (
    RegisterUserUseCase,
    RegisterUserCommand,
)
from accounts.domain.exceptions import (
    EmailAlreadyTakenException,
    InvalidCredentialsException,
    InvalidEmailException,
    InvalidTokenException,
    WeakPasswordException,
)
from accounts.infrastructure.password_policy import DjangoPasswordPolicy
from accounts.infrastructure.repositories import DjangoUserRepository
from accounts.infrastructure.token_service import SimpleJwtTokenService
from accounts.presentation.serializers import (
    CredentialsSerializer,
    RefreshSerializer,
    TokenPairSerializer,
)
from shared.presentation.responses import (
    INVALID_REQUEST_DETAILS,
    error_response,
    unexpected_error_response,
)

logger = logging.getLogger(__name__)


def _tokens_response(tokens: TokenPair, status_code: int) -> Response:
    return Response(TokenPairSerializer(tokens).data, status=status_code)


class PublicAPIView(APIView):
    """Base view for endpoints used without a valid access token."""

    authentication_classes = ()
    permission_classes = (AllowAny,)


class RegistrationView(PublicAPIView):
    @extend_schema(
        request=CredentialsSerializer,
        responses={
            201: TokenPairSerializer,
            400: OpenApiResponse(
                description="Invalid email, email already taken or weak password."
            ),
            500: OpenApiResponse(description="Unexpected server error."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = CredentialsSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                INVALID_REQUEST_DETAILS,
                status.HTTP_400_BAD_REQUEST,
                serializer.errors,
            )

        use_case = RegisterUserUseCase(
            users=DjangoUserRepository(),
            password_policy=DjangoPasswordPolicy(),
            tokens=SimpleJwtTokenService(),
        )
        command = RegisterUserCommand(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        try:
            tokens = use_case.execute(command)
        except (InvalidEmailException, EmailAlreadyTakenException) as error:
            return error_response(
                str(error), status.HTTP_400_BAD_REQUEST, {"email": [str(error)]}
            )
        except WeakPasswordException as error:
            return error_response(
                "Password is too weak.",
                status.HTTP_400_BAD_REQUEST,
                {"password": error.reasons},
            )
        except Exception:
            return unexpected_error_response(logger, "accounts API")

        return _tokens_response(tokens, status.HTTP_201_CREATED)


class LoginView(PublicAPIView):
    @extend_schema(
        request=CredentialsSerializer,
        responses={
            200: TokenPairSerializer,
            400: OpenApiResponse(description="Missing or invalid fields."),
            401: OpenApiResponse(description="Invalid email or password."),
            500: OpenApiResponse(description="Unexpected server error."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = CredentialsSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                INVALID_REQUEST_DETAILS,
                status.HTTP_400_BAD_REQUEST,
                serializer.errors,
            )

        use_case = LoginUserUseCase(
            users=DjangoUserRepository(), tokens=SimpleJwtTokenService()
        )
        command = LoginUserCommand(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        try:
            tokens = use_case.execute(command)
        except InvalidCredentialsException as error:
            return error_response(str(error), status.HTTP_401_UNAUTHORIZED)
        except Exception:
            return unexpected_error_response(logger, "accounts API")

        return _tokens_response(tokens, status.HTTP_200_OK)


class RefreshView(PublicAPIView):
    @extend_schema(
        request=RefreshSerializer,
        responses={
            200: TokenPairSerializer,
            400: OpenApiResponse(description="Missing refresh field."),
            401: OpenApiResponse(
                description="Refresh token is invalid, expired or already used."
            ),
            500: OpenApiResponse(description="Unexpected server error."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = RefreshSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                INVALID_REQUEST_DETAILS,
                status.HTTP_400_BAD_REQUEST,
                serializer.errors,
            )

        use_case = RefreshTokensUseCase(tokens=SimpleJwtTokenService())
        command = RefreshTokensCommand(
            refresh_token=serializer.validated_data["refresh"]
        )

        try:
            tokens = use_case.execute(command)
        except InvalidTokenException as error:
            return error_response(str(error), status.HTTP_401_UNAUTHORIZED)
        except Exception:
            return unexpected_error_response(logger, "accounts API")

        return _tokens_response(tokens, status.HTTP_200_OK)
