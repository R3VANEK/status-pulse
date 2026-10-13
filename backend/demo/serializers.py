from rest_framework import serializers
from demo.models import Program


class ProgramSerializer(serializers.ModelSerializer[Program]):
    class Meta:
        model = Program
        fields = ["id", "text"]
