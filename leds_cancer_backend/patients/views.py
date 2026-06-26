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
    """
    GET  /api/patients/       — list all patients (supports ?search=)
    POST /api/patients/       — create a new patient
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        query = request.query_params.get("search", "").strip()
        patients = _repo.search(query) if query else _repo.get_all()
        serializer = PatientListSerializer(patients, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
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
    """
    GET    /api/patients/{id}/  — retrieve patient with exams
    PUT    /api/patients/{id}/  — full update
    PATCH  /api/patients/{id}/  — partial update
    DELETE /api/patients/{id}/  — remove patient
    """

    permission_classes = [IsAuthenticated]

    def _get_patient_or_404(self, patient_id: int) -> Response | object:
        patient = _repo.get_by_id(patient_id)
        if patient is None:
            return Response({"detail": "Paciente não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        return patient

    def get(self, request: Request, pk: int) -> Response:
        result = self._get_patient_or_404(pk)
        if isinstance(result, Response):
            return result
        return Response(PatientDetailSerializer(result).data)

    def put(self, request: Request, pk: int) -> Response:
        result = self._get_patient_or_404(pk)
        if isinstance(result, Response):
            return result
        serializer = PatientWriteSerializer(result, data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = _repo.update(result, **serializer.validated_data)
        return Response(PatientDetailSerializer(patient).data)

    def patch(self, request: Request, pk: int) -> Response:
        result = self._get_patient_or_404(pk)
        if isinstance(result, Response):
            return result
        serializer = PatientWriteSerializer(result, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        patient = _repo.update(result, **serializer.validated_data)
        return Response(PatientDetailSerializer(patient).data)

    def delete(self, request: Request, pk: int) -> Response:
        result = self._get_patient_or_404(pk)
        if isinstance(result, Response):
            return result
        _repo.delete(result)  # type: ignore[arg-type]
        return Response(status=status.HTTP_204_NO_CONTENT)
