from django.db import models


class PatientStatus(models.TextChoices):
    """Status possíveis de um paciente no sistema."""

    ATIVO = "ativo", "Ativo"
    INATIVO = "inativo", "Inativo"


class Patient(models.Model):
    """Representa um paciente cadastrado no sistema LEDS Cancer.

    Datas são armazenadas como campos ``DateField`` nativos do Django;
    a API as serializa no formato ``dd/MM/yyyy`` para corresponder ao
    contrato esperado pelo frontend.

    Attributes:
        name: Nome completo do paciente.
        birth_date: Data de nascimento.
        cpf: CPF formatado (``000.000.000-00``), único no sistema.
        phone: Telefone de contato (opcional).
        email: E-mail de contato (opcional).
        status: Situação atual (``ativo`` ou ``inativo``).
        created_at: Data/hora de criação do registro (automático).
        updated_at: Data/hora da última atualização (automático).
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
