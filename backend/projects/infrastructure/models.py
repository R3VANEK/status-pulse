from uuid import uuid4
from django.db import models
from django.utils import timezone
from projects.domain.enums import ProjectStatus


class Project(models.Model):
    ProjectStatusChoices = models.TextChoices(
        "ProjectStatusChoices",
        [(status.name, status.value) for status in ProjectStatus],
    )

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=200, null=True)
    status = models.CharField(max_length=20, choices=ProjectStatusChoices)
    created_at = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="project_deadline_after_creation",
                condition=models.Q(deadline__gte=models.F("created_at")),
            ),
        ]
