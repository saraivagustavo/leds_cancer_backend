from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    MEDICO = "medico", "Médico(a)"
    TECNICO = "tecnico", "Técnico(a)"
    ADMINISTRADOR = "administrador", "Administrador(a)"


class User(AbstractUser):
    """
    Custom user model. Uses email as the primary login identifier.
    CRM field covers doctors and general professional ID for other roles.
    """

    email = models.EmailField(unique=True)
    crm = models.CharField(max_length=50, unique=True, null=True, blank=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.MEDICO,
    )
    # is_active=False means "pending admin approval" after registration
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        db_table = "auth_user_custom"

    def __str__(self) -> str:
        return f"{self.get_full_name()} ({self.email})"
