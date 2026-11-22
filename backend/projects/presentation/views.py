import logging
from typing import Any
from uuid import UUID, uuid4

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.application.use_cases import delete_attachment, upload_attachment
from projects.domain.value_objects import MAX_ATTACHMENT_FILE_SIZE_BYTES
from projects.infrastructure.repositories import (
    DjangoProjectAttachmentRepository,
    DjangoProjectRepository,
)

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
                {"details": "No file provided in the 'file' form field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content = uploaded.read(MAX_ATTACHMENT_FILE_SIZE_BYTES + 1)
        if len(content) > MAX_ATTACHMENT_FILE_SIZE_BYTES:
            return Response(
                {
                    "details": "Invalid project attachment: file size must be at most 5MB."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        command = upload_attachment.Command(
            actor_id=request.user.id,
            project_id=project_uuid,
            file_name=uploaded.name,
            content=content,
            content_type=uploaded.content_type or "application/octet-stream",
            content_size=len(content),
        )
        use_case = upload_attachment.UseCase(
            projects=DjangoProjectRepository,
            attachments=DjangoProjectAttachmentRepository,
        )
        result = use_case.execute(command)

        return Response(
            {
                "id": str(result.id),
                "project": str(result.project_id),
                "file_name": result.file_name,
                "upload_date": result.upload_date.isoformat(),
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
        project_id: UUID,
        attachment_id: UUID,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        "delete project attachment"

        command = delete_attachment.Command(
            actor_id=uuid4(),  # MOCK
            project_id=project_id,
            attachment_id=attachment_id,
        )
        use_case = delete_attachment.UseCase(
            projects=DjangoProjectRepository,
            attachments=DjangoProjectAttachmentRepository,
        )
        use_case.execute(command)

        return Response(status=status.HTTP_204_NO_CONTENT)
