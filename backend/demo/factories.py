from factory.django import DjangoModelFactory
from demo.models import Program
import factory

from uuid import uuid4


class ProgramFactory(DjangoModelFactory[Program]):
    class Meta:
        model = Program

    id = factory.LazyFunction(uuid4)  # type: ignore
    text = "foo"
