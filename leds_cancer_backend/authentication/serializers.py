from typing import Any

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, UserRole
from .repositories import UserRepository

_user_repo = UserRepository()


# ─── Leitura ──────────────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    """Read-only representation returned after login / profile fetch."""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "full_name", "email", "crm", "role")
        read_only_fields = fields

    def get_full_name(self, obj: User) -> str:
        return obj.get_full_name() or obj.username


# ─── Registro ─────────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    crm = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    role = serializers.ChoiceField(choices=UserRole.choices)
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    def validate_email(self, value: str) -> str:
        if _user_repo.get_by_email(value):
            raise serializers.ValidationError("Este e-mail já está em uso.")
        return value

    def validate_crm(self, value: str) -> str:
        if value and _user_repo.get_by_crm(value):
            raise serializers.ValidationError("Este CRM já está em uso.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "As senhas não coincidem."})
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        full_name: str = validated_data["full_name"]
        parts = full_name.strip().split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""

        base_username = validated_data["email"].split("@")[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        return _user_repo.create(
            username=username,
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=first_name,
            last_name=last_name,
            crm=validated_data.get("crm") or None,
            role=validated_data["role"],
            is_active=False,
        )


# ─── Atualização de perfil ────────────────────────────────────────────────────

class UpdateProfileSerializer(serializers.ModelSerializer):
    """PATCH /api/auth/me/update/ — update name, email, crm."""

    full_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    crm = serializers.CharField(max_length=50, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("full_name", "email", "crm")

    def validate_email(self, value: str) -> str:
        user = self.context["request"].user
        existing = _user_repo.get_by_email(value)
        if existing and existing.pk != user.pk:
            raise serializers.ValidationError("Este e-mail já está em uso.")
        return value

    def validate_crm(self, value: str) -> str:
        user = self.context["request"].user
        existing = _user_repo.get_by_crm(value)
        if value and existing and existing.pk != user.pk:
            raise serializers.ValidationError("Este CRM já está em uso.")
        return value

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        full_name = validated_data.pop("full_name", None)
        if full_name is not None:
            parts = full_name.strip().split(" ", 1)
            instance.first_name = parts[0]
            instance.last_name = parts[1] if len(parts) > 1 else ""
        for attr, value in validated_data.items():
            setattr(instance, attr, value or None)
        instance.save()
        return instance


# ─── Alteração de senha ───────────────────────────────────────────────────────

class UpdatePasswordSerializer(serializers.Serializer):
    """POST /api/auth/me/password/ — change password."""

    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value: str) -> str:
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "As senhas não coincidem."})
        return attrs


# ─── Login JWT customizado ────────────────────────────────────────────────────

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Overrides JWT login to allow identifier = email OR crm.
    The frontend sends { identifier, password }.
    """

    username_field = "identifier"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields.pop("username", None)
        self.fields["identifier"] = serializers.CharField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        identifier: str = attrs.get("identifier", "")
        password: str = attrs.get("password", "")

        user = _user_repo.get_by_identifier(identifier)

        if user is None or not user.check_password(password):
            raise serializers.ValidationError("Credenciais inválidas.")

        if not user.is_active:
            raise serializers.ValidationError(
                "Conta pendente de aprovação pelo administrador."
            )

        refresh = self.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
        }
