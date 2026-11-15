from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.response import Response
from projects.infrastructure.factories import ProjectFactory
from projects.infrastructure.models import Project as ProjectModel
from rest_framework.response import Response
from typing import cast

URL = "/api/projects/"


class CreateProjectTests(APITestCase):

    def test_creates_project(self) -> None:

        deadline = timezone.now() + timedelta(days=7)

        response = self.client.post(
            URL,
            {
                "name": "Status pulse",
                "deadline": deadline.isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        projects = ProjectModel.objects.all()
        self.assertEqual(len(projects), 1)
        project = projects[0]
        self.assertEqual(project.name, "Status pulse")
        self.assertEqual(project.description, None)
        self.assertAlmostEqual(
            project.created_at, timezone.now(), delta=timedelta(seconds=10)
        )
        self.assertEqual(project.deadline, deadline)
        self.assertEqual(project.status, "planned")


class ListProjectsTests(APITestCase):

    def test_lists_projects(self) -> None:

        ProjectFactory.create_batch(3)

        response = cast(Response, self.client.get(URL))
        assert response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(response.data["limit"], settings.PROJECTS_DEFAULT_PAGE_SIZE)
        self.assertEqual(response.data["offset"], 0)
        self.assertEqual(len(response.data["results"]), 3)

    def test_lists_projects_with_pagination(self) -> None:
        ProjectFactory.create_batch(5)

        response = cast(Response, self.client.get(URL, {"limit": 2, "offset": 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 5)
        self.assertEqual(response.data["limit"], 2)
        self.assertEqual(response.data["offset"], 1)
        self.assertEqual(len(response.data["results"]), 2)

    def test_lists_empty_collection(self) -> None:
        response = cast(Response, self.client.get(URL))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])

    def test_rejects_invalid_pagination_params(self) -> None:
        cases = [
            {"limit": "abc"},
            {"limit": 0},
            {"limit": settings.PROJECTS_MAX_PAGE_SIZE + 1},
            {"offset": -1},
        ]
        for params in cases:
            with self.subTest(params=params):
                response = cast(Response, self.client.get(URL, params))

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("details", response.data)
                self.assertIn("errors", response.data)

    def test_rejects_invalid_payload(self) -> None:
        response = self.client.post(URL, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("details", response.data)
        self.assertEqual(set(response.data["errors"]), {"name", "deadline"})
        self.assertEqual(ProjectModel.objects.count(), 0)
