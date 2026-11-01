from allauth.account.models import EmailAddress
from django.contrib.auth import authenticate
from django.db import IntegrityError, transaction

from accounts.application.interfaces import UserRepository
from accounts.domain.entities import User
from accounts.domain.exceptions import EmailAlreadyTaken
from accounts.domain.value_objects import Email
from accounts.infrastructure.models import User as UserModel


class DjangoUserRepository(UserRepository):
    def exists_with_email(self, email: Email) -> bool:
        return (
            UserModel.objects.filter(email__iexact=email.value).exists()
            or EmailAddress.objects.filter(email__iexact=email.value).exists()
        )

    def create(self, email: Email, password: str) -> User:
        try:
            with transaction.atomic():
                model = UserModel.objects.create_user(
                    email=email.value, password=password
                )
                # Register the address in allauth, so its email features
                # (verification, managing addresses) know about it.
                EmailAddress.objects.create(
                    user=model, email=email.value, primary=True, verified=False
                )
        except IntegrityError as error:
            # Another request registered the same email in the meantime.
            raise EmailAlreadyTaken(email.value) from error
        return self._to_entity(model)

    def get_by_credentials(self, email: Email, password: str) -> User | None:
        model = authenticate(request=None, username=email.value, password=password)
        if not isinstance(model, UserModel):
            return None
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(id=model.pk, email=Email(model.email), is_active=model.is_active)
