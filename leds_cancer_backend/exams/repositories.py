from typing import Optional

from django.db.models import Q, QuerySet

from .models import Exam, ExamStatus


class ExamRepository:
    """
    Encapsulates all database operations for the Exam model.
    Views and services should never call Exam.objects directly.
    """

    def get_all(self) -> QuerySet[Exam]:
        return Exam.objects.select_related("patient", "radiologist").all()

    def get_by_id(self, exam_id: int) -> Optional[Exam]:
        return (
            Exam.objects.select_related("patient", "radiologist")
            .filter(pk=exam_id)
            .first()
        )

    def get_by_patient(self, patient_id: int) -> QuerySet[Exam]:
        return (
            Exam.objects.select_related("patient", "radiologist")
            .filter(patient_id=patient_id)
            .order_by("-exam_date")
        )

    def get_recent(self, limit: int = 20) -> QuerySet[Exam]:
        return self.get_all().order_by("-created_at")[:limit]

    def get_pending(self) -> QuerySet[Exam]:
        return self.get_all().filter(status=ExamStatus.PENDENTE)

    def search(self, query: str) -> QuerySet[Exam]:
        """Search by patient name, requesting physician or technique."""
        return (
            Exam.objects.select_related("patient", "radiologist")
            .filter(
                Q(patient__name__icontains=query)
                | Q(requesting_physician__icontains=query)
            )
        )

    def filter_by_status(self, status: str) -> QuerySet[Exam]:
        return self.get_all().filter(status=status)

    def create(self, **data: object) -> Exam:
        exam = Exam(**data)
        exam.save()
        return exam

    def update(self, exam: Exam, **fields: object) -> Exam:
        for attr, value in fields.items():
            setattr(exam, attr, value)
        exam.save(update_fields=list(fields.keys()) + ["updated_at"])
        return exam

    def delete(self, exam: Exam) -> None:
        exam.delete()

    # ── Dashboard stats ───────────────────────────────────────────────────────

    def count_today(self) -> int:
        from django.utils import timezone
        today = timezone.localdate()
        return Exam.objects.filter(exam_date=today).count()

    def count_pending(self) -> int:
        return Exam.objects.filter(status=ExamStatus.PENDENTE).count()

    def count_concluded_today(self) -> int:
        from django.utils import timezone
        today = timezone.localdate()
        return Exam.objects.filter(
            status=ExamStatus.CONCLUIDO, exam_date=today
        ).count()

    def count_current_month(self) -> int:
        from django.utils import timezone
        now = timezone.now()
        return Exam.objects.filter(
            exam_date__year=now.year, exam_date__month=now.month
        ).count()
