from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .repositories import UserRepository
from .serializers import (
    CustomTokenObtainPairSerializer,
    PhysicianSerializer,
    RegisterSerializer,
    UpdatePasswordSerializer,
    UpdateProfileSerializer,
    UserSerializer,
)

_TAG = "Autenticação"
_repo = UserRepository()


@extend_schema(
    tags=[_TAG],
    summary="Login",
    description="Autentica via e-mail ou CRM. Retorna access + refresh token e dados do usuário.",
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    tags=[_TAG],
    summary="Cadastro",
    description="Cria um novo usuário com status pendente. Requer aprovação do administrador.",
    request=RegisterSerializer,
    responses={201: {"type": "object", "properties": {"detail": {"type": "string"}}}},
)
class RegisterView(APIView):
    permission_classes: list = []

    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Cadastro realizado! Aguarde a aprovação do administrador."},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=[_TAG],
    summary="Meu perfil",
    responses=UserSerializer,
)
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(UserSerializer(request.user).data)


@extend_schema_view(
    put=extend_schema(
        tags=[_TAG],
        summary="Atualizar perfil",
        request=UpdateProfileSerializer,
        responses=UserSerializer,
    ),
    patch=extend_schema(
        tags=[_TAG],
        summary="Atualizar perfil (parcial)",
        request=UpdateProfileSerializer,
        responses=UserSerializer,
    ),
)
class UpdateProfileView(APIView):
    """PUT/PATCH /api/auth/me/update/ — update name, email, crm."""

    permission_classes = [IsAuthenticated]

    def _save(self, request: Request, partial: bool) -> Response:
        serializer = UpdateProfileSerializer(
            request.user, data=request.data, partial=partial, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)

    def put(self, request: Request) -> Response:
        return self._save(request, partial=False)

    def patch(self, request: Request) -> Response:
        return self._save(request, partial=True)


@extend_schema(
    tags=[_TAG],
    summary="Alterar senha",
    request=UpdatePasswordSerializer,
    responses={200: {"type": "object", "properties": {"detail": {"type": "string"}}}},
)
class UpdatePasswordView(APIView):
    """POST /api/auth/me/password/ — change current user password."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = UpdatePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])  # type: ignore[union-attr]
        request.user.save(update_fields=["password"])  # type: ignore[union-attr]
        return Response({"detail": "Senha alterada com sucesso."})


@extend_schema(
    tags=[_TAG],
    summary="Listar médicos/técnicos ativos",
    description="Retorna todos os usuários ativos com role médico ou técnico. Usado pelo autocomplete do frontend.",
    responses=PhysicianSerializer(many=True),
)
class PhysicianListView(APIView):
    """GET /api/auth/users/ — list of active physicians for autocomplete."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        users = _repo.get_active_physicians()
        return Response(PhysicianSerializer(users, many=True).data)
