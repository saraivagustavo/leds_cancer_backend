from typing import Optional

from django.db.models import Q, QuerySet

from .models import Patient, PatientStatus


class PatientRepository:
    """Camada de acesso a dados para o modelo ``Patient``.

    Centraliza todas as queries do banco referentes a pacientes.
    Views e serviços **não devem** chamar ``Patient.objects`` diretamente.
    """

    def get_all(self) -> QuerySet[Patient]:
        """Retorna todos os pacientes, ordenados por nome.

        Returns:
            QuerySet de todos os ``Patient``.
        """
        return Patient.objects.all()

    def get_active(self) -> QuerySet[Patient]:
        """Retorna apenas os pacientes com status ``ativo``.

        Returns:
            QuerySet de ``Patient`` ativos.
        """
        return Patient.objects.filter(status=PatientStatus.ATIVO)

    def get_by_id(self, patient_id: int) -> Optional[Patient]:
        """Retorna o paciente com o ID informado, ou ``None``.

        Args:
            patient_id: Chave primária do paciente.

        Returns:
            Instância de ``Patient`` ou ``None``.
        """
        return Patient.objects.filter(pk=patient_id).first()

    def get_by_cpf(self, cpf: str) -> Optional[Patient]:
        """Busca paciente pelo CPF exato.

        Args:
            cpf: CPF formatado (``000.000.000-00``).

        Returns:
            Instância de ``Patient`` ou ``None``.
        """
        return Patient.objects.filter(cpf=cpf).first()

    def search(self, query: str) -> QuerySet[Patient]:
        """Busca pacientes por nome, CPF ou e-mail (case-insensitive).

        Usa ``OR`` para combinar os três campos, permitindo que o
        frontend faça buscas genéricas com um único termo.

        Args:
            query: Termo de busca.

        Returns:
            QuerySet de ``Patient`` que correspondem à query.
        """
        return Patient.objects.filter(
            Q(name__icontains=query)
            | Q(cpf__icontains=query)
            | Q(email__icontains=query)
        )

    def create(self, **data: object) -> Patient:
        """Cria e persiste um novo paciente.

        Args:
            **data: Pares ``campo=valor`` compatíveis com ``Patient``.

        Returns:
            Nova instância de ``Patient`` salva.
        """
        patient = Patient(**data)
        patient.save()
        return patient

    def update(self, patient: Patient, **fields: object) -> Patient:
        """Atualiza campos específicos de um paciente e persiste.

        Inclui ``updated_at`` automaticamente no ``update_fields``.

        Args:
            patient: Instância de ``Patient`` a atualizar.
            **fields: Pares ``campo=valor`` a atualizar.

        Returns:
            Instância de ``Patient`` atualizada.
        """
        for attr, value in fields.items():
            setattr(patient, attr, value)
        patient.save(update_fields=list(fields.keys()) + ["updated_at"])
        return patient

    def delete(self, patient: Patient) -> None:
        """Remove o paciente do banco de dados.

        Args:
            patient: Instância de ``Patient`` a remover.
        """
        patient.delete()
