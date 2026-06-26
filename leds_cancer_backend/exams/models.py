from django.conf import settings
from django.db import models

from patients.models import Patient


class ExamStatus(models.TextChoices):
    PENDENTE = "pendente", "Pendente"
    EM_ANALISE = "em_analise", "Em análise"
    CONCLUIDO = "concluido", "Concluído"
    CANCELADO = "cancelado", "Cancelado"


class ExamTechnique(models.TextChoices):
    DIGITAL = "digital", "Mamografia Digital"
    TOMOSSINTESE = "3d_tomossintese", "Mamografia 3D (Tomossíntese)"
    CONTRASTE = "contraste", "Mamografia com Contraste"


class BreastSide(models.TextChoices):
    ESQUERDA = "esquerda", "Esquerda"
    DIREITA = "direita", "Direita"
    BILATERAL = "bilateral", "Bilateral"


class Exam(models.Model):
    """
    Represents a mammography exam ordered for a patient.
    The image_file is stored server-side (media upload).
    """

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="exams",
        verbose_name="Paciente",
    )
    exam_date = models.DateField(verbose_name="Data do exame")
    technique = models.CharField(
        max_length=20,
        choices=ExamTechnique.choices,
        default=ExamTechnique.DIGITAL,
        verbose_name="Técnica",
    )
    breast_side = models.CharField(
        max_length=10,
        choices=BreastSide.choices,
        verbose_name="Lado",
    )
    clinical_history = models.TextField(blank=True, default="", verbose_name="Histórico clínico")
    requesting_physician = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Médico solicitante",
    )
    image_file = models.ImageField(
        upload_to="exams/images/%Y/%m/",
        null=True,
        blank=True,
        verbose_name="Imagem",
    )
    status = models.CharField(
        max_length=15,
        choices=ExamStatus.choices,
        default=ExamStatus.PENDENTE,
        verbose_name="Status",
    )
    # Doctor/technician who performed the analysis
    radiologist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analyzed_exams",
        verbose_name="Radiologista",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Exame"
        verbose_name_plural = "Exames"
        db_table = "exams_exam"
        ordering = ["-exam_date", "-created_at"]

    @property
    def exam_type(self) -> str:
        return self.get_technique_display()  # type: ignore[return-value]

    @property
    def radiologist_name(self) -> str:
        if self.radiologist:
            return self.radiologist.get_full_name() or self.radiologist.username
        return "Aguardando atribuição"

    def __str__(self) -> str:
        return f"{self.patient.name} — {self.exam_type} ({self.exam_date})"
