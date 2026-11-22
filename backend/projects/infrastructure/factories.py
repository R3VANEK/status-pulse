import mimetypes
from datetime import timedelta
from random import choice, random
from typing import Any, cast
from uuid import uuid4

import factory
from django.core.files.base import ContentFile
from django.core.files.storage import InMemoryStorage
from django.db.models.fields.files import FieldFile, FileField
from django.utils import timezone
from factory.django import DjangoModelFactory
from faker import Factory as FakerFactory

from projects.infrastructure.models import Project, ProjectAttachment
from shared.infrastructure.models import instance_hash_path

faker = FakerFactory.create()


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

    status = factory.LazyFunction(lambda: choice(list(Project.ProjectStatusChoices)))


def _read_source_file(source: Any) -> tuple[bytes, str, str]:
    """Extract content, name and content type from a caller-provided file."""
    name = getattr(source, "name", None) or f"{uuid4().hex}.txt"
    content_type = (
        getattr(source, "content_type", None)
        or mimetypes.guess_type(name)[0]
        or "application/octet-stream"
    )

    if hasattr(source, "seek"):
        try:
            source.seek(0)
        except (OSError, ValueError):
            pass

    content = source.read()
    if isinstance(content, str):
        content = content.encode()

    return content, name, content_type


def _make_file(
    project: Project,
    file_name: str,
    content: bytes,
    save_to_s3: bool,
) -> ContentFile | FieldFile:
    if save_to_s3:
        return ContentFile(content, name=file_name)

    storage = InMemoryStorage()
    name = storage.save(
        instance_hash_path(ProjectAttachment(project=project), file_name),
        ContentFile(content, name=file_name),
    )
    field = cast(FileField, ProjectAttachment._meta.get_field("file"))
    file = FieldFile(instance=None, field=field, name=name)
    file.storage = storage
    file.file = ContentFile(content, name=name)
    file._committed = True
    return file


class ProjectAttachmentFactory(DjangoModelFactory[ProjectAttachment]):
    SAVE_TO_S3 = False

    class Meta:
        model = ProjectAttachment
        exclude = ("content", "SAVE_TO_S3")
        rename = {"source_file": "file"}

    class Params:
        save_to_s3 = factory.LazyFunction(lambda: ProjectAttachmentFactory.SAVE_TO_S3)

    id = factory.LazyFunction(uuid4)  # type: ignore

    project = factory.SubFactory(ProjectFactory)

    content = factory.LazyFunction(lambda: faker.text(max_nb_chars=100).encode())
    file_name = factory.LazyFunction(lambda: f"{uuid4().hex}.txt")
    content_type = "text/plain"
    content_size = factory.LazyAttribute(lambda obj: len(obj.content))

    source_file = factory.LazyAttribute(
        lambda obj: _make_file(
            project=obj.project,
            file_name=obj.file_name,
            content=obj.content,
            save_to_s3=obj.save_to_s3,
        )
    )

    @classmethod
    def _adjust_kwargs(cls, **kwargs: Any) -> dict[str, Any]:
        provided_file = kwargs.pop("file", None)
        if provided_file is None:
            return kwargs

        content, file_name, content_type = _read_source_file(provided_file)
        kwargs.update(
            content=content,
            file_name=file_name,
            content_type=content_type,
            content_size=len(content),
        )
        kwargs["source_file"] = _make_file(
            project=kwargs["project"],
            file_name=file_name,
            content=content,
            save_to_s3=kwargs.get("save_to_s3", cls.SAVE_TO_S3),
        )
        return kwargs
