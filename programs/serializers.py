from rest_framework import serializers
from .models import Program, ProgramParticipation


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ["id", "name", "description"]


class ProgramParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramParticipation
        fields = ["id", "company", "program", "year"]


class ProgramParticipationReadSerializer(serializers.ModelSerializer):
    program = ProgramSerializer(read_only=True)

    class Meta:
        model = ProgramParticipation
        fields = ["id", "year", "program"]
