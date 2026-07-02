from typing import Any

from rest_framework import serializers

from .models import Patient, PatientStatus
from .repositories import PatientRepository

_patient_repo = PatientRepository()

DATE_FORMAT = "%d/%m/%Y"


class PatientExamSummarySerializer(serializers.Serializer):
    """Serializer read-only de resumo de exame aninhado no detalhe do paciente.

    Populado a partir do app ``exams`` — importado de forma lazy para
    evitar imports circulares entre os dois apps.
    """

    id = serializers.CharField()
    date = serializers.DateField(format=DATE_FORMAT, input_formats=[DATE_FORMAT, "%Y-%m-%d"])
    type = serializers.CharField(source="exam_type")
    status = serializers.CharField()
    radiologist = serializers.CharField(source="radiologist_name")


class PatientListSerializer(serializers.ModelSerializer):
    """Serializer leve usado no endpoint de listagem de pacientes.

    Inclui campos calculados dinamicamente:
    - ``age``: idade atual em anos completos.
    - ``last_exam``: data do exame mais recente no formato ``dd/MM/yyyy``.
    - ``total_exams``: quantidade total de exames do paciente.
    """

    birth_date = serializers.DateField(format=DATE_FORMAT, input_formats=[DATE_FORMAT, "%Y-%m-%d"])
    last_exam = serializers.SerializerMethodField()
    total_exams = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = (
            "id", "name", "birth_date", "age", "cpf",
            "phone", "email", "status", "last_exam", "total_exams",
        )

    def get_age(self, obj: Patient) -> int:
        """Calcula a idade em anos considerando se o aniversário já passou."""
        from datetime import date
        today = date.today()
        b = obj.birth_date
        return today.year - b.year - ((today.month, today.day) < (b.month, b.day))

    def get_last_exam(self, obj: Patient) -> str | None:
        """Retorna a data do exame mais recente ou ``None`` se não houver."""
        exam = obj.exams.order_by("-exam_date").first()  # type: ignore[attr-defined]
        if exam is None:
            return None
        return exam.exam_date.strftime(DATE_FORMAT)

    def get_total_exams(self, obj: Patient) -> int:
        """Retorna o total de exames vinculados ao paciente."""
        return obj.exams.count()  # type: ignore[attr-defined]


class PatientDetailSerializer(PatientListSerializer):
    """Serializer completo com lista de exames aninhados.

    Estende ``PatientListSerializer`` adicionando o campo ``exams``
    com o histórico completo serializado via ``ExamSummaryForPatientSerializer``.
    """

    exams = serializers.SerializerMethodField()

    class Meta(PatientListSerializer.Meta):
        fields = PatientListSerializer.Meta.fields + ("exams",)

    def get_exams(self, obj: Patient) -> list[dict[str, Any]]:
        """Retorna a lista de exames do paciente ordenada por data decrescente."""
        from exams.serializers import ExamSummaryForPatientSerializer
        qs = obj.exams.order_by("-exam_date")  # type: ignore[attr-defined]
        return ExamSummaryForPatientSerializer(qs, many=True).data


class PatientWriteSerializer(serializers.ModelSerializer):
    """Serializer usado nas operações de criação e atualização de pacientes.

    Valida a unicidade do CPF ignorando o próprio paciente em edições.
    """

    birth_date = serializers.DateField(format=DATE_FORMAT, input_formats=[DATE_FORMAT, "%Y-%m-%d"])

    class Meta:
        model = Patient
        fields = ("name", "birth_date", "cpf", "phone", "email", "status")

    def validate_cpf(self, value: str) -> str:
        """Rejeita CPF já cadastrado para outro paciente.

        Args:
            value: CPF a validar.

        Returns:
            O próprio CPF se válido.

        Raises:
            ValidationError: Se o CPF já estiver em uso por outro registro.
        """
        instance = self.instance
        existing = _patient_repo.get_by_cpf(value)
        if existing and (instance is None or existing.pk != instance.pk):
            raise serializers.ValidationError("CPF já cadastrado.")
        return value
