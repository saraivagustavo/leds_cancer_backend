from typing import Optional

from django.db.models import Q, QuerySet

from .models import Patient, PatientStatus


class PatientRepository:
    """
    Encapsulates all database operations for the Patient model.
    Views and services should never call Patient.objects directly.
    """

    def get_all(self) -> QuerySet[Patient]:
        return Patient.objects.all()

    def get_active(self) -> QuerySet[Patient]:
        return Patient.objects.filter(status=PatientStatus.ATIVO)

    def get_by_id(self, patient_id: int) -> Optional[Patient]:
        return Patient.objects.filter(pk=patient_id).first()

    def get_by_cpf(self, cpf: str) -> Optional[Patient]:
        return Patient.objects.filter(cpf=cpf).first()

    def search(self, query: str) -> QuerySet[Patient]:
        """Search patients by name, CPF or email."""
        return Patient.objects.filter(
            Q(name__icontains=query)
            | Q(cpf__icontains=query)
            | Q(email__icontains=query)
        )

    def create(self, **data: object) -> Patient:
        patient = Patient(**data)
        patient.save()
        return patient

    def update(self, patient: Patient, **fields: object) -> Patient:
        for attr, value in fields.items():
            setattr(patient, attr, value)
        patient.save(update_fields=list(fields.keys()) + ["updated_at"])
        return patient

    def delete(self, patient: Patient) -> None:
        patient.delete()
