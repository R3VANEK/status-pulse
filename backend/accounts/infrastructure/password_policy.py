from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from accounts.application.interfaces import PasswordPolicy
from accounts.domain.exceptions import WeakPassword
from accounts.domain.value_objects import Email
from accounts.infrastructure.models import User as UserModel


class DjangoPasswordPolicy(PasswordPolicy):
    def validate(self, password: str, email: Email) -> None:
        # Unsaved user instance, only so validators can compare the password with the email.
        candidate = UserModel(email=email.value)
        try:
            validate_password(password, user=candidate)
        except ValidationError as error:
            raise WeakPassword(list(error.messages)) from error
