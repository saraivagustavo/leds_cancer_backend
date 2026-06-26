from django.db import models


class PatientStatus(models.TextChoices):
    ATIVO = "ativo", "Ativo"
    INATIVO = "inativo", "Inativo"


class Patient(models.Model):
    """
    Represents a patient in the system.
    Dates are stored as proper Date fields; the API serializes them as dd/MM/yyyy
    to match the frontend contract.
    """

    name = models.CharField(max_length=200)
    birth_date = models.DateField()
    cpf = models.CharField(max_length=14, unique=True)  # formatted: 000.000.000-00
    phone = models.CharField(max_length=20, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    status = models.CharField(
        max_length=10,
        choices=PatientStatus.choices,
        default=PatientStatus.ATIVO,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        db_table = "patients_patient"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
