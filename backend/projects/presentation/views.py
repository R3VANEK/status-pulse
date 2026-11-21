from typing import Any
from uuid import UUID, uuid4
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from projects.infrastructure.models import Project, ProjectAttachment

from projects.application.use_cases import delete_attachment

from projects.infrastructure.repositories import (
    DjangoProjectRepository,
    DjangoProjectAttachmentRepository,
)
import logging

LOGGER = logging.getLogger("projects")


class ProjectAttachmentGeneralView(APIView):
    def post(
        self,
        request: Request,
        project_uuid: UUID,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """Upload attachment to a project."""
        uploaded = request.FILES.get("file")
        if uploaded is None:
            return Response(
                {"detail": "No file provided in the 'file' form field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = Project.objects.get(id=project_uuid)
        except Project.DoesNotExist:
            return Response(
                {"detail": f"Project '{project_uuid}' does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        attachment = ProjectAttachment.objects.create(
            project=project,
            file_name=uploaded.name,
            file=uploaded,
        )
        return Response(
            {
                "id": str(attachment.id),
                "project": str(attachment.project_id),
                "file_name": attachment.file_name,
                "upload_date": attachment.upload_date.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )


class ProjectAttachmentDetailView(APIView):
    def get(
        self,
        request: Request,
        project_uuid: UUID,
        attachment_uuid: UUID,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """downloads the attachment as a file"""
        ...

    def delete(
        self,
        request: Request,
        project_uuid: UUID,
        attachment_uuid: UUID,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        "delete project attachment"

        command = delete_attachment.Command(
            actor_id=uuid4(),  # MOCK
            project_id=project_uuid,
            attachment_id=attachment_uuid,
        )

        use_case = delete_attachment.UseCase(
            projects=DjangoProjectRepository,
            attachments=DjangoProjectAttachmentRepository,
        )

        use_case.execute(command)

        return Response(status=status.HTTP_204_NO_CONTENT)
