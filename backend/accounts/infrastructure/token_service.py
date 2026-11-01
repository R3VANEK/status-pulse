from rest_framework.exceptions import APIException
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.application.interfaces import TokenPair, TokenService
from accounts.domain.entities import User
from accounts.domain.exceptions import InvalidToken
from accounts.infrastructure.models import User as UserModel


class SimpleJwtTokenService(TokenService):
    def issue_for(self, user: User) -> TokenPair:
        if user.id is None:
            raise ValueError("Cannot issue tokens for a user that is not saved yet.")
        model = UserModel.objects.get(pk=user.id)
        refresh = RefreshToken.for_user(model)
        return TokenPair(access=str(refresh.access_token), refresh=str(refresh))

    def refresh(self, refresh_token: str) -> TokenPair:
        # Reuse simplejwt's own refresh logic: signature and expiry check,
        # blacklist check, rotation and blacklisting of the used token.
        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except (TokenError, APIException) as error:
            raise InvalidToken() from error

        data = serializer.validated_data
        return TokenPair(
            access=data["access"], refresh=data.get("refresh", refresh_token)
        )
