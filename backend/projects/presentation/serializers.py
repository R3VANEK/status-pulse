from django.conf import settings
from rest_framework import serializers

from projects.domain.enums import ProjectStatus


class CreateProjectSerializer(serializers.Serializer):
    """Request body of POST /projects/."""

    name = serializers.CharField(max_length=60)
    description = serializers.CharField(
        max_length=200, required=False, allow_null=True, allow_blank=True
    )
    deadline = serializers.DateTimeField()


class ListProjectsQuerySerializer(serializers.Serializer):
    """Query params of GET /projects/."""

    limit = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=settings.PROJECTS_MAX_PAGE_SIZE,
        default=settings.PROJECTS_DEFAULT_PAGE_SIZE,
    )
    offset = serializers.IntegerField(required=False, min_value=0, default=0)


class ProjectSerializer(serializers.Serializer):
    """Representation of a single project."""

    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    status = serializers.ChoiceField(
        read_only=True,
        choices=[(status.value, status.value) for status in ProjectStatus],
    )
    deadline = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class ProjectPageSerializer(serializers.Serializer):
    """A single page of projects."""

    count = serializers.IntegerField(read_only=True, source="total")
    limit = serializers.IntegerField(read_only=True)
    offset = serializers.IntegerField(read_only=True)
    results = ProjectSerializer(many=True, read_only=True, source="items")
