from rest_framework import status
from rest_framework.test import APITestCase
from uuid import uuid4
from demo.models import Program


class ProgramListTests(APITestCase):
    def test_list_programs(self) -> None:
        Program.objects.create(id=uuid4(), text="Program 1")
        Program.objects.create(id=uuid4(), text="Program 2")
        response = self.client.get("/api/programs")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_programs_allows_frontend_origin(self) -> None:
        response = self.client.get("/api/programs", HTTP_ORIGIN="http://localhost:3000")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.headers["Access-Control-Allow-Origin"], "http://localhost:3000"
        )

    def test_list_programs_rejects_unknown_origin(self) -> None:
        response = self.client.get("/api/programs", HTTP_ORIGIN="http://evil.example")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("Access-Control-Allow-Origin", response.headers)

    def test_preflight_allows_frontend_origin(self) -> None:
        response = self.client.options(
            "/api/programs",
            HTTP_ORIGIN="http://localhost:3000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.headers["Access-Control-Allow-Origin"], "http://localhost:3000"
        )
