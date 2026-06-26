from typing import Any

from rest_framework import serializers

from .models import Exam

DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%d/%m/%Y %H:%M"


class ExamSummaryForPatientSerializer(serializers.ModelSerializer):
    """
    Compact serializer used inside PatientDetailSerializer.
    Matches the PatientExam interface expected by the frontend.
    """

    date = serializers.DateField(source="exam_date", format=DATE_FORMAT)
    type = serializers.SerializerMethodField()
    radiologist = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ("id", "date", "type", "status", "radiologist")

    def get_type(self, obj: Exam) -> str:
        return obj.exam_type

    def get_radiologist(self, obj: Exam) -> str:
        return obj.radiologist_name


class RecentExamSerializer(serializers.ModelSerializer):
    """
    Serializer for the dashboard recent-exams list.
    Matches the RecentExam interface expected by the frontend.
    """

    patient_name = serializers.CharField(source="patient.name")
    datetime = serializers.SerializerMethodField()
    exam_type = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ("id", "patient_name", "datetime", "exam_type", "status")

    def get_datetime(self, obj: Exam) -> str:
        return obj.created_at.strftime(DATETIME_FORMAT)

    def get_exam_type(self, obj: Exam) -> str:
        return obj.exam_type


class ExamListSerializer(serializers.ModelSerializer):
    """Used in the history / exam list endpoints."""

    patient_id = serializers.IntegerField(source="patient.id")
    patient_name = serializers.CharField(source="patient.name")
    datetime = serializers.SerializerMethodField()
    exam_type = serializers.SerializerMethodField()
    radiologist = serializers.SerializerMethodField()
    breast_side = serializers.CharField()
    requesting_physician = serializers.CharField()
    clinical_history = serializers.CharField()

    class Meta:
        model = Exam
        fields = (
            "id",
            "patient_id",
            "patient_name",
            "datetime",
            "exam_type",
            "status",
            "radiologist",
            "breast_side",
            "requesting_physician",
            "clinical_history",
        )

    def get_datetime(self, obj: Exam) -> str:
        return obj.created_at.strftime(DATETIME_FORMAT)

    def get_exam_type(self, obj: Exam) -> str:
        return obj.exam_type

    def get_radiologist(self, obj: Exam) -> str:
        return obj.radiologist_name


class ExamWriteSerializer(serializers.ModelSerializer):
    """Used for create / update operations. Accepts image upload."""

    exam_date = serializers.DateField(
        format=DATE_FORMAT,
        input_formats=[DATE_FORMAT, "%Y-%m-%d"],
    )

    class Meta:
        model = Exam
        fields = (
            "patient",
            "exam_date",
            "technique",
            "breast_side",
            "clinical_history",
            "requesting_physician",
            "image_file",
            "status",
            "radiologist",
        )
        extra_kwargs = {
            "image_file": {"required": False},
            "status": {"required": False},
            "radiologist": {"required": False},
            "clinical_history": {"required": False},
            "requesting_physician": {"required": False},
        }


class DashboardStatsSerializer(serializers.Serializer):
    """Serializes the stats block returned by GET /api/dashboard/stats/."""

    today_patients = serializers.IntegerField()
    pending_exams = serializers.IntegerField()
    monthly_diagnostics = serializers.IntegerField()
    concluded_today = serializers.IntegerField()
