import logging

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.application.use_cases.create_project import (
    CreateProjectCommand,
    CreateProjectUseCase,
)
from projects.application.use_cases.list_projects import (
    ListProjectsCommand,
    ListProjectsUseCase,
)
from projects.domain.exceptions import InvalidProjectDeadlineException
from projects.infrastructure.repositories import DjangoProjectRepository
from projects.presentation.serializers import (
    CreateProjectSerializer,
    ListProjectsQuerySerializer,
    ProjectPageSerializer,
    ProjectSerializer,
)
from shared.presentation.responses import (
    INVALID_REQUEST_DETAILS,
    error_response,
    unexpected_error_response,
)

logger = logging.getLogger(__name__)


class ProjectGeneralView(APIView):
    """Lists the projects (GET) and creates a new one (POST)."""

    @extend_schema(
        parameters=[ListProjectsQuerySerializer],
        responses={
            200: ProjectPageSerializer,
            400: OpenApiResponse(description="Invalid limit or offset."),
            500: OpenApiResponse(description="Unexpected server error."),
        },
    )
    def get(self, request: Request) -> Response:
        query = ListProjectsQuerySerializer(data=request.query_params)
        if not query.is_valid():
            return error_response(
                INVALID_REQUEST_DETAILS,
                status.HTTP_400_BAD_REQUEST,
                query.errors,
            )

        use_case = ListProjectsUseCase(projects=DjangoProjectRepository())
        command = ListProjectsCommand(
            limit=query.validated_data["limit"],
            offset=query.validated_data["offset"],
        )

        try:
            page = use_case.execute(command)
        except Exception:
            return unexpected_error_response(logger, "projects API")

        return Response(ProjectPageSerializer(page).data, status=status.HTTP_200_OK)

    @extend_schema(
        request=CreateProjectSerializer,
        responses={
            201: ProjectSerializer,
            400: OpenApiResponse(description="Invalid project data or deadline."),
            500: OpenApiResponse(description="Unexpected server error."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = CreateProjectSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                INVALID_REQUEST_DETAILS,
                status.HTTP_400_BAD_REQUEST,
                serializer.errors,
            )

        use_case = CreateProjectUseCase(projects=DjangoProjectRepository())
        command = CreateProjectCommand(
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description"),
            deadline=serializer.validated_data["deadline"],
        )

        try:
            project = use_case.execute(command)
        except InvalidProjectDeadlineException as exc:
            return error_response(
                "project's deadline is invalid",
                status.HTTP_400_BAD_REQUEST,
                {"deadline": [str(exc)]},
            )
        except Exception:
            return unexpected_error_response(logger, "projects API")

        return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)
