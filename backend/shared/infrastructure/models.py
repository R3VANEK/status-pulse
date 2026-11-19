from django.db import models
from django.core.files.storage import Storage
from integrations.s3 import get_s3_client
from django.core.files import File
from abc import ABC, abstractmethod
from typing import ClassVar, Any
from django.utils.deconstruct import deconstructible


def instance_hash_path(instance: models.Model, filename: str):

    instance_hash = getattr(instance, "instance_hash", "")
    bucket_name = getattr(instance, "bucket_name")

    if bucket_name is None:
        raise Exception(f"no bucket_name param of {instance.__class__.__name__}")

    if instance_hash:
        return f"{bucket_name}/{instance_hash}/{filename}"
    else:
        return f"{bucket_name}/{filename}"


@deconstructible
class S3Storage(Storage):

    def _split_filename(self, name: str) -> tuple[str, str]:
        """since name is path like eg. projects/foo.txt we split bucket info, from filename"""
        name = name.strip()
        bucket = name.split("/")[0]
        filename = name[name.index("/") + 1 :]

        if bucket == filename:
            raise Exception(
                f"No bucket defined in the upload_to param of {self.__class__.__name__}"
            )

        return bucket, filename

    def _open(self, name: str, mode="rb") -> File:
        bucket, key = self._split_filename(name)
        return get_s3_client().get_file(bucket=bucket, key=key)

    def _save(self, name: str, content: Any) -> str:
        bucket, key = self._split_filename(name)
        return get_s3_client().save_file(bucket=bucket, key=key, content=content)

    def delete(self, name: str) -> None:
        bucket, key = self._split_filename(name)
        get_s3_client().delete_file(bucket=bucket, key=key)

    def exists(self, name: str) -> bool:
        bucket, key = self._split_filename(name)
        return get_s3_client().exists_file(bucket=bucket, key=key)


class S3FileField(models.FileField):

    def __init__(self, verbose_name=None, name=None, **kwargs) -> None:
        kwargs.setdefault("upload_to", instance_hash_path)
        kwargs.setdefault("storage", S3Storage())
        super().__init__(
            verbose_name=verbose_name,
            name=name,
            **kwargs,
        )
