import socket
from urllib.parse import urlparse
from uuid import UUID

from botocore.exceptions import ClientError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from integrations.s3 import get_s3_client
from projects.domain.enums import ProjectStatus
from projects.infrastructure.factories import ProjectFactory
from projects.infrastructure.models import ProjectAttachment


class UploadAttachmentEndpointS3IntegrationTests(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test-user",
            email="test@example.com",
            password="password123",
        )
        self.client.force_authenticate(self.user)
        self.project = ProjectFactory(status=ProjectStatus.PLANNED)
        self.storage = get_s3_client()
        self._ensure_storage_is_reachable()
        self._ensure_bucket_exists("projects")
        self.created_file_names: list[str] = []

    def tearDown(self) -> None:
        for file_name in self.created_file_names:
            try:
                bucket, key = file_name.split("/", 1)
                self.storage.delete_file(bucket=bucket, key=key)
            except Exception:
                pass
        super().tearDown()

    def get_url(self, project_id: UUID) -> str:
        return reverse(
            "project-attachments-general",
            kwargs={"project_uuid": project_id},
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
                "Start the storage with `docker compose -f docker-compose.test.yaml up -d s3`."
            )

    def _ensure_bucket_exists(self, bucket_name: str) -> None:
        try:
            self.storage.client.create_bucket(Bucket=bucket_name)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code not in {"BucketAlreadyOwnedByYou", "BucketAlreadyExists"}:
                raise

    def test_uploads_attachment_to_real_s3(self) -> None:
        uploaded = SimpleUploadedFile(
            "report.pdf",
            b"%PDF-1.4 test-content",
            content_type="application/pdf",
        )

        response = self.client.post(
            self.get_url(self.project.id),
            {"file": uploaded},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["project"], str(self.project.id))
        self.assertEqual(response.data["file_name"], "report.pdf")

        attachment = ProjectAttachment.objects.get(id=response.data["id"])
        self.created_file_names.append(attachment.file.name)

        self.assertEqual(attachment.content_type, "application/pdf")
        self.assertEqual(attachment.content_size, len(b"%PDF-1.4 test-content"))
        self.assertTrue(attachment.file.storage.exists(attachment.file.name))
        with attachment.file.open("rb") as stored_file:
            self.assertEqual(stored_file.read(), b"%PDF-1.4 test-content")


class UploadAttachmentEndpointValidationTests(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test-user",
            email="test@example.com",
            password="password123",
        )
        self.client.force_authenticate(self.user)
        self.project = ProjectFactory(status=ProjectStatus.PLANNED)

    def get_url(self, project_id: UUID) -> str:
        return reverse(
            "project-attachments-general",
            kwargs={"project_uuid": project_id},
        )

    def test_rejects_missing_file(self) -> None:
        response = self.client.post(
            self.get_url(self.project.id), {}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["details"], "No file provided in the 'file' form field."
        )

    def test_rejects_disallowed_extension(self) -> None:
        uploaded = SimpleUploadedFile(
            "malware.exe",
            b"MZ",
            content_type="application/octet-stream",
        )

        response = self.client.post(
            self.get_url(self.project.id),
            {"file": uploaded},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("file type '.exe' is not allowed", response.data["details"])

    def test_rejects_file_name_with_slash(self) -> None:
        uploaded = SimpleUploadedFile(
            "bad/name.pdf",
            b"content",
            content_type="application/pdf",
        )

        response = self.client.post(
            self.get_url(self.project.id),
            {"file": uploaded},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cannot contain slashes", response.data["details"])

    def test_rejects_too_long_file_name(self) -> None:
        uploaded = SimpleUploadedFile(
            "a" * 101,
            b"content",
            content_type="application/pdf",
        )

        response = self.client.post(
            self.get_url(self.project.id),
            {"file": uploaded},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("at most 100 characters", response.data["details"])

    def test_rejects_file_larger_than_5mb(self) -> None:
        uploaded = SimpleUploadedFile(
            "big.pdf",
            b"a" * (5 * 1024 * 1024 + 1),
            content_type="application/pdf",
        )

        response = self.client.post(
            self.get_url(self.project.id),
            {"file": uploaded},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["details"],
            "Invalid project attachment: file size must be at most 5MB.",
        )
