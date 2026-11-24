from uuid import UUID, uuid4

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from projects.domain.enums import ProjectStatus
from projects.infrastructure.factories import ProjectAttachmentFactory, ProjectFactory
from projects.infrastructure.models import ProjectAttachment
from shared.tests.base import S3BaseTest


class DeleteAttachmentEndpointS3IntegrationTests(APITestCase, S3BaseTest):
    def get_url(self, project_id: UUID, attachment_id: UUID) -> str:
        return reverse(
            "project-attachments-detail",
            kwargs={
                "project_id": project_id,
                "attachment_id": attachment_id,
            },
        )

    def test_deletes_attachment_from_db_and_s3(self) -> None:
        attachment = ProjectAttachmentFactory(
            save_to_s3=True,
            project=self.project,
            file=SimpleUploadedFile(
                "report.txt",
                b"hello there general kenobi",
                content_type="text/plain",
            ),
        )
        other_attachment = ProjectAttachmentFactory(
            save_to_s3=True,
            project=self.project,
            file=SimpleUploadedFile(
                "keep.txt",
                b"another attachment",
                content_type="text/plain",
            ),
        )

        file_name = attachment.file.name
        other_file_name = other_attachment.file.name
        self.created_file_names.extend([file_name, other_file_name])
        self.assert_s3_file_exists(file_name)
        self.assert_s3_file_exists(other_file_name)

        response = self.client.delete(
            self.get_url(self.project.id, attachment.id)
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ProjectAttachment.objects.filter(id=attachment.id).exists())
        self.assertEqual(
            list(ProjectAttachment.objects.values_list("id", flat=True)),
            [other_attachment.id],
        )
        self.assert_s3_file_does_not_exist(file_name)
        self.assert_s3_file_exists(other_file_name)


class DeleteAttachmentEndpointValidationTests(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test-user",
            email="test@example.com",
            password="password123",
        )
        self.client.force_authenticate(self.user)
        self.project = ProjectFactory(status=ProjectStatus.PLANNED)

    def get_url(self, project_id: UUID, attachment_id: UUID) -> str:
        return reverse(
            "project-attachments-detail",
            kwargs={
                "project_id": project_id,
                "attachment_id": attachment_id,
            },
        )

    def test_returns_404_when_project_does_not_exist(self) -> None:
        response = self.client.delete(
            self.get_url(project_id=uuid4(), attachment_id=uuid4())
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get("details"), "Specified project was not found"
        )

    def test_returns_404_when_attachment_does_not_exist(self) -> None:
        response = self.client.delete(
            self.get_url(project_id=self.project.id, attachment_id=uuid4())
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get("details"), "Specified project attachment was not found"
        )
