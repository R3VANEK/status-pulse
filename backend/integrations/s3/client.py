import boto3
from botocore.client import Config
from django.conf import settings
from threading import Lock


class MinioClient:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._client = None
        return cls._instance

    @property
    def client(self):
        if self._client is None:
            with self._lock:
                if self._client is None:
                    self._client = boto3.client(
                        "s3",
                        endpoint_url=settings.S3_ENDPOINT_URL,
                        aws_access_key_id=settings.MINIO_ROOT_USER,
                        aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
                        config=Config(
                            signature_version="s3v4", s3={"addressing_style": "path"}
                        ),
                        region_name="us-east-1",
                    )
        return self._client

    def delete_all_objects(self, bucket_name: str) -> int:

        s3 = MinioClient().client
        paginator = s3.get_paginator("list_objects_v2")
        deleted_objs: int = 0

        for page in paginator.paginate(Bucket=bucket_name):
            objects = page.get("Contents", [])

            if not objects:
                continue

            s3.delete_objects(
                Bucket=bucket_name,
                Delete={
                    "Objects": [{"Key": obj["Key"]} for obj in objects],
                    "Quiet": True,
                },
            )

            deleted_objs += 1

        return deleted_objs


def get_s3_client() -> MinioClient:
    return MinioClient()
