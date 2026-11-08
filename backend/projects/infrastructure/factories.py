from factory.django import DjangoModelFactory
from projects.infrastructure.models import Project
import factory
from faker import Factory
from uuid import uuid4
from random import random
from django.utils import timezone
from datetime import timedelta

faker = Factory.create()


class ProjectFactory(DjangoModelFactory[Project]):
    class Meta:
        model = Project

    id = factory.LazyFunction(uuid4)  # type: ignore

    name = faker.catch_phrase()

    description = factory.LazyFunction(
        lambda: faker.text(max_nb_chars=100) if random() <= 0.7 else None
    )

    deadline = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=random() * 30)
    )
