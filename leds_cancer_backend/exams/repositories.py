from typing import Optional

from django.db.models import Q, QuerySet

from .models import Exam, ExamStatus


class ExamRepository:
    """Camada de acesso a dados para o modelo ``Exam``.

    Centraliza todas as queries do banco referentes a exames.
    Views e serviços **não devem** chamar ``Exam.objects`` diretamente.
    Todas as queries que buscam exames por ID ou lista usam
    ``select_related("patient", "radiologist")`` para evitar N+1.
    """

    def get_all(self) -> QuerySet[Exam]:
        """Retorna todos os exames com ``patient`` e ``radiologist`` pré-carregados.

        Returns:
            QuerySet de todos os ``Exam``.
        """
        return Exam.objects.select_related("patient", "radiologist").all()

    def get_by_id(self, exam_id: int) -> Optional[Exam]:
        """Retorna o exame com o ID informado, ou ``None``.

        Args:
            exam_id: Chave primária do exame.

        Returns:
            Instância de ``Exam`` ou ``None``.
        """
        return (
            Exam.objects.select_related("patient", "radiologist")
            .filter(pk=exam_id)
            .first()
        )

    def get_by_patient(self, patient_id: int) -> QuerySet[Exam]:
        """Retorna exames de um paciente, ordenados por data decrescente.

        Args:
            patient_id: Chave primária do paciente.

        Returns:
            QuerySet de ``Exam`` do paciente.
        """
        return (
            Exam.objects.select_related("patient", "radiologist")
            .filter(patient_id=patient_id)
            .order_by("-exam_date")
        )

    def get_recent(self, limit: int = 20) -> QuerySet[Exam]:
        """Retorna os exames mais recentes por data de criação.

        Args:
            limit: Número máximo de resultados. Padrão: 20.

        Returns:
            QuerySet limitado de ``Exam``.
        """
        return self.get_all().order_by("-created_at")[:limit]

    def get_pending(self) -> QuerySet[Exam]:
        """Retorna exames com status ``pendente``.

        Returns:
            QuerySet de ``Exam`` pendentes.
        """
        return self.get_all().filter(status=ExamStatus.PENDENTE)

    def search(self, query: str) -> QuerySet[Exam]:
        """Busca exames por nome do paciente ou médico solicitante.

        Args:
            query: Termo de busca (case-insensitive).

        Returns:
            QuerySet de ``Exam`` que correspondem à query.
        """
        return (
            Exam.objects.select_related("patient", "radiologist")
            .filter(
                Q(patient__name__icontains=query)
                | Q(requesting_physician__icontains=query)
            )
        )

    def filter_by_status(self, status: str) -> QuerySet[Exam]:
        """Filtra exames pelo status informado.

        Args:
            status: Valor de ``ExamStatus`` a filtrar.

        Returns:
            QuerySet de ``Exam`` com o status informado.
        """
        return self.get_all().filter(status=status)

    def create(self, **data: object) -> Exam:
        """Cria e persiste um novo exame.

        Args:
            **data: Pares ``campo=valor`` compatíveis com ``Exam``.

        Returns:
            Nova instância de ``Exam`` salva.
        """
        exam = Exam(**data)
        exam.save()
        return exam

    def update(self, exam: Exam, **fields: object) -> Exam:
        """Atualiza campos específicos de um exame e persiste.

        Inclui ``updated_at`` automaticamente no ``update_fields``.

        Args:
            exam: Instância de ``Exam`` a atualizar.
            **fields: Pares ``campo=valor`` a atualizar.

        Returns:
            Instância de ``Exam`` atualizada.
        """
        for attr, value in fields.items():
            setattr(exam, attr, value)
        exam.save(update_fields=list(fields.keys()) + ["updated_at"])
        return exam

    def delete(self, exam: Exam) -> None:
        """Remove o exame do banco de dados.

        Args:
            exam: Instância de ``Exam`` a remover.
        """
        exam.delete()

    # ── Contadores para o dashboard ─────────────────────────────────────────

    def count_today(self) -> int:
        """Conta exames cuja ``exam_date`` é igual à data local de hoje.

        Returns:
            Número inteiro de exames de hoje.
        """
        from django.utils import timezone
        today = timezone.localdate()
        return Exam.objects.filter(exam_date=today).count()

    def count_pending(self) -> int:
        """Conta exames com status ``pendente``.

        Returns:
            Número inteiro de exames pendentes.
        """
        return Exam.objects.filter(status=ExamStatus.PENDENTE).count()

    def count_concluded_today(self) -> int:
        """Conta exames concluídos hoje.

        Returns:
            Número inteiro de exames com ``status=concluido`` e
            ``exam_date`` igual a hoje.
        """
        from django.utils import timezone
        today = timezone.localdate()
        return Exam.objects.filter(
            status=ExamStatus.CONCLUIDO, exam_date=today
        ).count()

    def count_current_month(self) -> int:
        """Conta exames do mês corrente.

        Returns:
            Número inteiro de exames no mês/ano atual.
        """
        from django.utils import timezone
        now = timezone.now()
        return Exam.objects.filter(
            exam_date__year=now.year, exam_date__month=now.month
        ).count()
