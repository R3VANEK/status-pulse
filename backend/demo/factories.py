from factory.django import DjangoModelFactory
from demo.models import Program
from uuid import uuid4
import factory


class ProgramFactory(DjangoModelFactory[Program]):
    class Meta:
        model = Program

    id = factory.LazyFunction(uuid4)  # type: ignore
    text = "foo"
