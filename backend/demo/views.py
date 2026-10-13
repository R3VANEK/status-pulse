from typing import Any
from demo.models import Program
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import mixins
from rest_framework import generics
from demo.serializers import ProgramSerializer


class ProgramList(mixins.ListModelMixin, generics.GenericAPIView[Program]):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self.list(request, *args, **kwargs)
