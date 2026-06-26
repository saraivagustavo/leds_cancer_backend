from typing import Any

from rest_framework import serializers

from .models import Patient, PatientStatus
from .repositories import PatientRepository

_patient_repo = PatientRepository()

DATE_FORMAT = "%d/%m/%Y"


class PatientExamSummarySerializer(serializers.Serializer):
    """
    Nested read-only exam summary serialized inside Patient detail.
    Populated from the exams app — imported lazily to avoid circular imports.
    """

    id = serializers.CharField()
    date = serializers.DateField(format=DATE_FORMAT, input_formats=[DATE_FORMAT, "%Y-%m-%d"])
    type = serializers.CharField(source="exam_type")
    status = serializers.CharField()
    radiologist = serializers.CharField(source="radiologist_name")


class PatientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer used in list endpoints."""

    birth_date = serializers.DateField(format=DATE_FORMAT, input_formats=[DATE_FORMAT, "%Y-%m-%d"])
    last_exam = serializers.SerializerMethodField()
    total_exams = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = (
            "id",
            "name",
            "birth_date",
            "age",
            "cpf",
            "phone",
            "email",
            "status",
            "last_exam",
            "total_exams",
        )

    def get_age(self, obj: Patient) -> int:
        from datetime import date
        today = date.today()
        b = obj.birth_date
        return today.year - b.year - ((today.month, today.day) < (b.month, b.day))

    def get_last_exam(self, obj: Patient) -> str | None:
        exam = obj.exams.order_by("-exam_date").first()  # type: ignore[attr-defined]
        if exam is None:
            return None
        return exam.exam_date.strftime(DATE_FORMAT)

    def get_total_exams(self, obj: Patient) -> int:
        return obj.exams.count()  # type: ignore[attr-defined]


class PatientDetailSerializer(PatientListSerializer):
    """Full serializer including nested exams list."""

    exams = serializers.SerializerMethodField()

    class Meta(PatientListSerializer.Meta):
        fields = PatientListSerializer.Meta.fields + ("exams",)

    def get_exams(self, obj: Patient) -> list[dict[str, Any]]:
        from exams.serializers import ExamSummaryForPatientSerializer
        qs = obj.exams.order_by("-exam_date")  # type: ignore[attr-defined]
        return ExamSummaryForPatientSerializer(qs, many=True).data


class PatientWriteSerializer(serializers.ModelSerializer):
    """Used for create / update operations."""

    birth_date = serializers.DateField(format=DATE_FORMAT, input_formats=[DATE_FORMAT, "%Y-%m-%d"])

    class Meta:
        model = Patient
        fields = ("name", "birth_date", "cpf", "phone", "email", "status")

    def validate_cpf(self, value: str) -> str:
        instance = self.instance
        existing = _patient_repo.get_by_cpf(value)
        if existing and (instance is None or existing.pk != instance.pk):
            raise serializers.ValidationError("CPF já cadastrado.")
        return value
