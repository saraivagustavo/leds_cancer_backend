from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .repositories import ExamRepository
from .serializers import (
    DashboardStatsSerializer,
    ExamImageTokenSerializer,
    ExamListSerializer,
    ExamWriteSerializer,
    RecentExamSerializer,
)
from .tokens import generate_token, verify_token

_repo = ExamRepository()
_TAG_EXAMS = "Exames"
_TAG_DASHBOARD = "Dashboard"


@extend_schema_view(
    get=extend_schema(
        tags=[_TAG_EXAMS],
        summary="Listar exames",
        description="Suporta filtros: ?search=, ?status=, ?patient=",
        responses=ExamListSerializer(many=True),
    ),
    post=extend_schema(
        tags=[_TAG_EXAMS],
        summary="Criar exame",
        request=ExamWriteSerializer,
        responses={201: ExamListSerializer},
    ),
)
class ExamListCreateView(APIView):
    """
    GET  /api/exams/   — list exams (supports ?search=, ?status=, ?patient=)
    POST /api/exams/   — create a new exam (multipart for image upload)
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request: Request) -> Response:
        search = request.query_params.get("search", "").strip()
        status_filter = request.query_params.get("status", "").strip()
        patient_id = request.query_params.get("patient", "").strip()

        if patient_id:
            exams = _repo.get_by_patient(int(patient_id))
        elif search:
            exams = _repo.search(search)
        elif status_filter:
            exams = _repo.filter_by_status(status_filter)
        else:
            exams = _repo.get_all()

        return Response(ExamListSerializer(exams, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = ExamWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        exam = _repo.create(**serializer.validated_data)
        return Response(
            ExamListSerializer(exam).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    get=extend_schema(
        tags=[_TAG_EXAMS],
        summary="Detalhe do exame",
        responses=ExamListSerializer,
    ),
    put=extend_schema(
        tags=[_TAG_EXAMS],
        summary="Atualizar exame (completo)",
        request=ExamWriteSerializer,
        responses=ExamListSerializer,
    ),
    patch=extend_schema(
        tags=[_TAG_EXAMS],
        summary="Atualizar exame (parcial)",
        request=ExamWriteSerializer,
        responses=ExamListSerializer,
    ),
    delete=extend_schema(
        tags=[_TAG_EXAMS],
        summary="Remover exame",
        responses={204: None},
    ),
)
class ExamDetailView(APIView):
    """
    GET    /api/exams/{id}/  — retrieve exam detail
    PUT    /api/exams/{id}/  — full update
    PATCH  /api/exams/{id}/  — partial update (e.g. status change)
    DELETE /api/exams/{id}/  — remove exam
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def _get_or_404(self, exam_id: int) -> Response | object:
        exam = _repo.get_by_id(exam_id)
        if exam is None:
            return Response({"detail": "Exame não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        return exam

    def get(self, request: Request, pk: int) -> Response:
        result = self._get_or_404(pk)
        if isinstance(result, Response):
            return result
        return Response(ExamListSerializer(result).data)

    def put(self, request: Request, pk: int) -> Response:
        result = self._get_or_404(pk)
        if isinstance(result, Response):
            return result
        serializer = ExamWriteSerializer(result, data=request.data)
        serializer.is_valid(raise_exception=True)
        exam = _repo.update(result, **serializer.validated_data)  # type: ignore[arg-type]
        return Response(ExamListSerializer(exam).data)

    def patch(self, request: Request, pk: int) -> Response:
        result = self._get_or_404(pk)
        if isinstance(result, Response):
            return result
        serializer = ExamWriteSerializer(result, data=request.data, partial=True)  # type: ignore[arg-type]
        serializer.is_valid(raise_exception=True)
        exam = _repo.update(result, **serializer.validated_data)  # type: ignore[arg-type]
        return Response(ExamListSerializer(exam).data)

    def delete(self, request: Request, pk: int) -> Response:
        result = self._get_or_404(pk)
        if isinstance(result, Response):
            return result
        _repo.delete(result)  # type: ignore[arg-type]
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=[_TAG_EXAMS],
    summary="Exames recentes",
    description="Últimos exames para o feed do dashboard. Suporta ?limit=N",
    responses=RecentExamSerializer(many=True),
)
class RecentExamsView(APIView):
    """GET /api/exams/recent/ — last 20 exams for the dashboard feed."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        limit = int(request.query_params.get("limit", 20))
        exams = _repo.get_recent(limit=limit)
        return Response(RecentExamSerializer(exams, many=True).data)


@extend_schema(
    tags=[_TAG_DASHBOARD],
    summary="Estatísticas do dashboard",
    responses=DashboardStatsSerializer,
)
class DashboardStatsView(APIView):
    """GET /api/dashboard/stats/ — counters consumed by stat cards."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        data = {
            "today_patients": _repo.count_today(),
            "pending_exams": _repo.count_pending(),
            "monthly_diagnostics": _repo.count_current_month(),
            "concluded_today": _repo.count_concluded_today(),
        }
        serializer = DashboardStatsSerializer(data)
        return Response(serializer.data)


# ─── Image token ──────────────────────────────────────────────────────────────

@extend_schema(
    tags=[_TAG_EXAMS],
    summary="Gerar token de acesso à imagem",
    description=(
        "Gera um token HMAC temporário (padrão: 15 min) que permite a um "
        "serviço externo buscar a imagem do exame sem precisar de JWT. "
        "Requer autenticação do usuário solicitante."
    ),
    responses=ExamImageTokenSerializer,
)
class ExamImageTokenView(APIView):
    """POST /api/exams/{id}/image-token/ — issue a short-lived HMAC token."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, pk: int) -> Response:
        exam = _repo.get_by_id(pk)
        if exam is None:
            return Response({"detail": "Exame não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if not exam.image_file:
            return Response(
                {"detail": "Este exame não possui imagem associada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        token, expires_ts = generate_token(pk)
        serializer = ExamImageTokenSerializer({"token": token, "expires_at": expires_ts})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ─── Image download (serviço externo) ────────────────────────────────────────

@extend_schema(
    tags=[_TAG_EXAMS],
    summary="Baixar imagem do exame via token HMAC",
    description=(
        "Endpoint público (sem JWT) para serviços externos baixarem a imagem. "
        "Requer os query params `token` (HMAC hex) e `expires` (Unix timestamp). "
        "O token deve ter sido gerado por POST /api/exams/{id}/image-token/."
    ),
    responses={(200, "image/*"): {}},
)
class ExamImageDownloadView(APIView):
    """GET /api/exams/{id}/image/?token=<hmac>&expires=<ts>"""

    permission_classes: list = []  # autenticação feita via HMAC

    def get(self, request: Request, pk: int) -> Response:
        from django.http import FileResponse

        token = request.query_params.get("token", "")
        expires_raw = request.query_params.get("expires", "")

        # ── Valida parâmetros ──────────────────────────────────────────────
        if not token or not expires_raw:
            return Response(
                {"detail": "Parâmetros 'token' e 'expires' são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            expires_ts = int(expires_raw)
        except ValueError:
            return Response(
                {"detail": "Parâmetro 'expires' deve ser um inteiro (Unix timestamp)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Verifica HMAC ──────────────────────────────────────────────────
        if not verify_token(pk, token, expires_ts):
            return Response(
                {"detail": "Token inválido ou expirado."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # ── Busca o exame e a imagem ───────────────────────────────────────
        exam = _repo.get_by_id(pk)
        if exam is None:
            return Response({"detail": "Exame não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if not exam.image_file:
            return Response(
                {"detail": "Este exame não possui imagem associada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ── Serve o arquivo ────────────────────────────────────────────────
        try:
            image = exam.image_file.open("rb")
        except FileNotFoundError:
            return Response(
                {"detail": "Arquivo de imagem não encontrado no servidor."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return FileResponse(
            image,
            as_attachment=False,
            filename=exam.image_file.name.split("/")[-1],
        )
