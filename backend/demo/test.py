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
