import mimetypes
from datetime import timedelta
from random import choice, random, randrange
from typing import Any, cast
from uuid import uuid4
import random
import factory
from django.core.files.base import ContentFile
from django.core.files.storage import InMemoryStorage
from django.db.models.fields.files import FieldFile, FileField
from django.utils import timezone
from factory.django import DjangoModelFactory
from faker import Factory as FakerFactory

from accounts.infrastructure.models import User
from shared.infrastructure.models import instance_hash_path

faker = FakerFactory.create()


class UserFactory(DjangoModelFactory[User]):

    class Meta:
        model = User

    id = factory.LazyFunction(uuid4)  # type: ignore

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    first_name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    phone_number = factory.Faker("numerify", text="#########")
    is_active = True
    is_staff = False
    date_joined = factory.LazyFunction(
        lambda: timezone.now() - timedelta(days=random.randrange(0, 60))
    )

    password = factory.PostGenerationMethodCall("set_password", "password")
