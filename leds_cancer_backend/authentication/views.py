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
    """POST /api/auth/token/ — login por e-mail ou CRM.

    Delega a lógica ao ``CustomTokenObtainPairSerializer``, que aceita
    o campo ``identifier`` (e-mail ou CRM) em vez de ``username``.
    """

    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    tags=[_TAG],
    summary="Cadastro",
    description="Cria um novo usuário com status pendente. Requer aprovação do administrador.",
    request=RegisterSerializer,
    responses={201: {"type": "object", "properties": {"detail": {"type": "string"}}}},
)
class RegisterView(APIView):
    """POST /api/auth/register/ — cadastro público de novos usuários.

    Qualquer pessoa pode se registrar. A conta criada fica inativa
    (``is_active=False``) até que um administrador a aprove no painel.
    """

    permission_classes: list = []

    def post(self, request: Request) -> Response:
        """Valida os dados e cria o usuário inativo.

        Args:
            request: Requisição com ``full_name``, ``email``, ``crm``,
                ``role``, ``password`` e ``confirm_password``.

        Returns:
            HTTP 201 com mensagem de confirmação.
        """
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
    """GET /api/auth/me/ — retorna os dados do usuário autenticado."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Serializa e retorna o usuário da sessão atual.

        Args:
            request: Requisição autenticada via JWT.

        Returns:
            HTTP 200 com os dados do usuário.
        """
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
    """PUT/PATCH /api/auth/me/update/ — atualiza nome, e-mail e/ou CRM."""

    permission_classes = [IsAuthenticated]

    def _save(self, request: Request, partial: bool) -> Response:
        """Valida e persiste as alterações de perfil.

        Args:
            request: Requisição com os campos a atualizar.
            partial: Se ``True``, campos omitidos são mantidos.

        Returns:
            HTTP 200 com o perfil atualizado.
        """
        serializer = UpdateProfileSerializer(
            request.user, data=request.data, partial=partial, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)

    def put(self, request: Request) -> Response:
        """Atualização completa do perfil (todos os campos obrigatórios)."""
        return self._save(request, partial=False)

    def patch(self, request: Request) -> Response:
        """Atualização parcial do perfil (apenas os campos enviados)."""
        return self._save(request, partial=True)


@extend_schema(
    tags=[_TAG],
    summary="Alterar senha",
    request=UpdatePasswordSerializer,
    responses={200: {"type": "object", "properties": {"detail": {"type": "string"}}}},
)
class UpdatePasswordView(APIView):
    """POST /api/auth/me/password/ — troca a senha do usuário autenticado."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Valida a senha atual e aplica a nova.

        Args:
            request: Requisição com ``current_password``, ``new_password``
                e ``confirm_password``.

        Returns:
            HTTP 200 com mensagem de confirmação.
        """
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
    """GET /api/auth/users/ — lista médicos e técnicos ativos.

    Usado pelo componente ``PhysicianAutocomplete`` do frontend para
    popular as sugestões do campo "Médico Solicitante" com dados reais
    em vez de uma lista mockada.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Retorna a lista de profissionais elegíveis.

        Args:
            request: Requisição autenticada via JWT.

        Returns:
            HTTP 200 com lista de ``PhysicianSerializer``.
        """
        users = _repo.get_active_physicians()
        return Response(PhysicianSerializer(users, many=True).data)
