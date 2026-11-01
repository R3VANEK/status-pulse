from rest_framework import serializers


class CredentialsSerializer(serializers.Serializer):
    """Request body of /registration and /login."""

    email = serializers.CharField(max_length=254)
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class RefreshSerializer(serializers.Serializer):
    """Request body of /refresh."""

    refresh = serializers.CharField()


class TokenPairSerializer(serializers.Serializer):
    """Response body with a pair of JWT tokens."""

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
