from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.application.interfaces import TokenPair
from accounts.application.use_cases.log_in_user import LogInUser, LogInUserCommand
from accounts.application.use_cases.refresh_tokens import (
    RefreshTokens,
    RefreshTokensCommand,
)
from accounts.application.use_cases.register_user import (
    RegisterUser,
    RegisterUserCommand,
)
from accounts.domain.exceptions import (
    EmailAlreadyTaken,
    InvalidCredentials,
    InvalidEmail,
    InvalidToken,
    WeakPassword,
)
from accounts.infrastructure.password_policy import DjangoPasswordPolicy
from accounts.infrastructure.repositories import DjangoUserRepository
from accounts.infrastructure.token_service import SimpleJwtTokenService
from accounts.presentation.serializers import (
    CredentialsSerializer,
    RefreshSerializer,
    TokenPairSerializer,
)


def _tokens_response(tokens: TokenPair, status_code: int) -> Response:
    return Response(TokenPairSerializer(tokens).data, status=status_code)


class PublicAPIView(APIView):
    """Base view for endpoints used without a valid access token."""

    # Do not even try to read the "Authorization" header here: an expired
    # access token sent by the client must not block registration or refresh.
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
        },
    )
    def post(self, request: Request) -> Response:
        serializer = CredentialsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case = RegisterUser(
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
        except (InvalidEmail, EmailAlreadyTaken) as error:
            return Response({"email": [str(error)]}, status=status.HTTP_400_BAD_REQUEST)
        except WeakPassword as error:
            return Response(
                {"password": error.reasons}, status=status.HTTP_400_BAD_REQUEST
            )

        return _tokens_response(tokens, status.HTTP_201_CREATED)


class LoginView(PublicAPIView):
    @extend_schema(
        request=CredentialsSerializer,
        responses={
            200: TokenPairSerializer,
            401: OpenApiResponse(description="Invalid email or password."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = CredentialsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case = LogInUser(
            users=DjangoUserRepository(), tokens=SimpleJwtTokenService()
        )
        command = LogInUserCommand(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        try:
            tokens = use_case.execute(command)
        except InvalidCredentials as error:
            return Response({"detail": str(error)}, status=status.HTTP_401_UNAUTHORIZED)

        return _tokens_response(tokens, status.HTTP_200_OK)


class RefreshView(PublicAPIView):
    @extend_schema(
        request=RefreshSerializer,
        responses={
            200: TokenPairSerializer,
            401: OpenApiResponse(
                description="Refresh token is invalid, expired or already used."
            ),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case = RefreshTokens(tokens=SimpleJwtTokenService())
        command = RefreshTokensCommand(
            refresh_token=serializer.validated_data["refresh"]
        )

        try:
            tokens = use_case.execute(command)
        except InvalidToken as error:
            return Response({"detail": str(error)}, status=status.HTTP_401_UNAUTHORIZED)

        return _tokens_response(tokens, status.HTTP_200_OK)
