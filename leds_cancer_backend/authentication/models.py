from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    """Papéis disponíveis para usuários do sistema."""

    MEDICO = "medico", "Médico(a)"
    TECNICO = "tecnico", "Técnico(a)"
    ADMINISTRADOR = "administrador", "Administrador(a)"


class User(AbstractUser):
    """Modelo de usuário customizado do sistema LEDS Cancer.

    Estende AbstractUser do Django adicionando campos de perfil
    profissional e um fluxo de aprovação manual por administrador.

    O login aceita ``username``, mas o ``CustomTokenObtainPairSerializer``
    permite autenticar também via ``email`` ou ``crm``.

    Attributes:
        email: Endereço de e-mail único do usuário.
        crm: Registro profissional (CRM para médicos, matrícula para
            técnicos). Opcional e único quando informado.
        role: Papel do usuário no sistema (ver ``UserRole``).
        is_active: ``False`` por padrão — indica conta pendente de
            aprovação pelo administrador. Após aprovação passa a ``True``.
    """

    email = models.EmailField(unique=True)
    crm = models.CharField(max_length=50, unique=True, null=True, blank=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.MEDICO,
    )
    # is_active=False significa "pendente de aprovação pelo admin"
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        db_table = "auth_user_custom"

    def __str__(self) -> str:
        return f"{self.get_full_name()} ({self.email})"
