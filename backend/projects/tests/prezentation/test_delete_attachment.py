from uuid import uuid4, UUID

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from projects.domain.enums import ProjectStatus
from projects.infrastructure.factories import ProjectFactory


class DeleteAttachmentEndpointTests(APITestCase):
    def get_url(self, project_id: UUID, attachment_id: UUID) -> str:
        return reverse(
            "project-attachments-detail",
            kwargs={
                "project_id": project_id,
                "attachment_id": attachment_id,
            },
        )

    def test_deleting_non_existent_attachment_returns_404(self) -> None:

        breakpoint()
        url = self.get_url(project_id=uuid4(), attachment_id=uuid4())
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get("details"), "Specified project was not found"
        )

        project = ProjectFactory(status=ProjectStatus.PLANNED)

        url = self.get_url(project_id=project.id, attachment_id=uuid4())
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get("details"), "Specified project attachment was not found"
        )
