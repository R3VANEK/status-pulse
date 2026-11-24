import socket
from urllib.parse import urlparse

from botocore.exceptions import ClientError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.testcases import TestCase

from integrations.s3 import get_s3_client
from projects.domain.enums import ProjectStatus
from projects.infrastructure.factories import ProjectFactory


class S3BaseTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test-user",
            email="test@example.com",
            password="password123",
        )
        if hasattr(self.client, "force_authenticate"):
            self.client.force_authenticate(self.user)

        self.project = ProjectFactory(status=ProjectStatus.PLANNED)
        self.storage = get_s3_client()
        self._ensure_storage_is_reachable()

        self.bucket_names = (
            settings.S3_PROJECT_ATTACHMENT_BUCKET_NAME,
            settings.S3_TASK_ATTACHMENT_BUCKET_NAME,
        )
        for bucket_name in self.bucket_names:
            self._ensure_bucket_exists(bucket_name)

        self.created_file_names: list[str] = []

    def tearDown(self) -> None:
        for file_name in self.created_file_names:
            try:
                bucket, key = self._split_file_name(file_name)
                self.storage.delete_file(bucket=bucket, key=key)
            except Exception:
                pass
        super().tearDown()

    @staticmethod
    def _split_file_name(file_name: str) -> tuple[str, str]:
        bucket, separator, key = file_name.strip().partition("/")
        if not separator or not bucket or not key:
            raise ValueError(f"Invalid S3 file name: {file_name!r}")
        return bucket, key

    def assert_s3_file_exists(self, file_name: str) -> None:
        bucket, key = self._split_file_name(file_name)
        self.assertTrue(
            self.storage.exists_file(bucket=bucket, key=key),
            f"Expected S3 object {file_name!r} to exist.",
        )

    def assert_s3_file_does_not_exist(self, file_name: str) -> None:
        bucket, key = self._split_file_name(file_name)
        self.assertFalse(
            self.storage.exists_file(bucket=bucket, key=key),
            f"Expected S3 object {file_name!r} to be deleted.",
        )

    def _ensure_storage_is_reachable(self) -> None:
        endpoint = settings.S3_ENDPOINT_URL
        parsed = urlparse(endpoint)
        host = parsed.hostname or "localhost"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        try:
            with socket.create_connection((host, port), timeout=5):
                pass
        except OSError as error:
            self.fail(
                f"S3 endpoint {endpoint} is not reachable ({error}). "
                "Start the storage with "
                "`docker compose -f docker-compose.test.yaml up -d s3`."
            )

    def _ensure_bucket_exists(self, bucket_name: str) -> None:
        try:
            self.storage.client.create_bucket(Bucket=bucket_name)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code not in {"BucketAlreadyOwnedByYou", "BucketAlreadyExists"}:
                raise
