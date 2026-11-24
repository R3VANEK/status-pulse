from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from projects.domain.enums import ProjectStatus
from projects.infrastructure.factories import ProjectFactory
from projects.infrastructure.models import ProjectAttachment
from shared.tests.base import S3BaseTest


class UploadAttachmentEndpointS3IntegrationTests(APITestCase, S3BaseTest):
    def get_url(self, project_id: UUID) -> str:
        return reverse(
            "project-attachments-general",
            kwargs={"project_uuid": project_id},
        )

    def test_uploads_attachment(self) -> None:
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
        self.assert_s3_file_exists(attachment.file.name)
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

    def test_sanitizes_file_name_with_slash(self) -> None:
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

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["file_name"], "name.pdf")
        self.assertNotIn("/", response.data["file_name"])

        attachment = ProjectAttachment.objects.get(id=response.data["id"])
        attachment.file.delete(save=False)

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
