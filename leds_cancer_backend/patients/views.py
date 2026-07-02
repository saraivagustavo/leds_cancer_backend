from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .repositories import PatientRepository
from .serializers import PatientDetailSerializer, PatientListSerializer, PatientWriteSerializer

_repo = PatientRepository()
_TAG = "Pacientes"


@extend_schema_view(
    get=extend_schema(
        tags=[_TAG],
        summary="Listar pacientes",
        description="Retorna todos os pacientes. Suporta filtro via ?search=.",
        responses=PatientListSerializer(many=True),
    ),
    post=extend_schema(
        tags=[_TAG],
        summary="Criar paciente",
        request=PatientWriteSerializer,
        responses={201: PatientDetailSerializer},
    ),
)
class PatientListCreateView(APIView):
    """Listagem e criação de pacientes.

    GET  /api/patients/  — lista todos; suporta ``?search=`` (nome/CPF/e-mail).
    POST /api/patients/  — cria um novo paciente.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Lista pacientes, com busca opcional.

        Args:
            request: Aceita ``?search=<termo>`` como query param.

        Returns:
            HTTP 200 com lista serializada por ``PatientListSerializer``.
        """
        query = request.query_params.get("search", "").strip()
        patients = _repo.search(query) if query else _repo.get_all()
        serializer = PatientListSerializer(patients, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """Cria um novo paciente com os dados fornecidos.

        Args:
            request: Corpo com ``name``, ``birth_date``, ``cpf``,
                ``phone``, ``email`` e ``status``.

        Returns:
            HTTP 201 com o paciente criado via ``PatientDetailSerializer``.
        """
        serializer = PatientWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = _repo.create(**serializer.validated_data)
        return Response(
            PatientDetailSerializer(patient).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    get=extend_schema(
        tags=[_TAG],
        summary="Detalhe do paciente",
        responses=PatientDetailSerializer,
    ),
    put=extend_schema(
        tags=[_TAG],
        summary="Atualizar paciente (completo)",
        request=PatientWriteSerializer,
        responses=PatientDetailSerializer,
    ),
    patch=extend_schema(
        tags=[_TAG],
        summary="Atualizar paciente (parcial)",
        request=PatientWriteSerializer,
        responses=PatientDetailSerializer,
    ),
    delete=extend_schema(
        tags=[_TAG],
        summary="Remover paciente",
        responses={204: None},
    ),
)
class PatientDetailView(APIView):
    """Operações sobre um paciente específico.

    GET    /api/patients/{id}/  — detalhe com exames aninhados.
    PUT    /api/patients/{id}/  — atualização completa.
    PATCH  /api/patients/{id}/  — atualização parcial.
    DELETE /api/patients/{id}/  — remoção.
    """

    permission_classes = [IsAuthenticated]

    def _get_patient_or_404(self, patient_id: int) -> Response | object:
        """Busca o paciente ou retorna HTTP 404.

        Args:
            patient_id: Chave primária do paciente.

        Returns:
            Instância de ``Patient`` ou ``Response`` 404.
        """
        patient = _repo.get_by_id(patient_id)
        if patient is None:
            return Response({"detail": "Paciente não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        return patient

    def get(self, request: Request, pk: int) -> Response:
        """Retorna o detalhe do paciente incluindo a lista de exames."""
        result = self._get_patient_or_404(pk)
        if isinstance(result, Response):
            return result
        return Response(PatientDetailSerializer(result).data)

    def put(self, request: Request, pk: int) -> Response:
        """Atualização completa — todos os campos são obrigatórios."""
        result = self._get_patient_or_404(pk)
        if isinstance(result, Response):
            return result
        serializer = PatientWriteSerializer(result, data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = _repo.update(result, **serializer.validated_data)
        return Response(PatientDetailSerializer(patient).data)

    def patch(self, request: Request, pk: int) -> Response:
        """Atualização parcial — apenas os campos enviados são alterados."""
        result = self._get_patient_or_404(pk)
        if isinstance(result, Response):
            return result
        serializer = PatientWriteSerializer(result, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        patient = _repo.update(result, **serializer.validated_data)
        return Response(PatientDetailSerializer(patient).data)

    def delete(self, request: Request, pk: int) -> Response:
        """Remove o paciente permanentemente do banco de dados."""
        result = self._get_patient_or_404(pk)
        if isinstance(result, Response):
            return result
        _repo.delete(result)  # type: ignore[arg-type]
        return Response(status=status.HTTP_204_NO_CONTENT)
