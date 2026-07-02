from typing import Optional

from django.contrib.auth.hashers import make_password
from django.db.models import QuerySet

from .models import User


class UserRepository:
    """Camada de acesso a dados para o modelo ``User``.

    Centraliza todas as queries do banco referentes a usuários.
    Views e serviços **não devem** chamar ``User.objects`` diretamente —
    toda interação com o banco deve passar por esta classe.
    """

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Retorna o usuário com o ID informado, ou ``None`` se não existir.

        Args:
            user_id: Chave primária do usuário.

        Returns:
            Instância de ``User`` ou ``None``.
        """
        return User.objects.filter(pk=user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por e-mail (case-insensitive).

        Args:
            email: Endereço de e-mail a ser pesquisado.

        Returns:
            Instância de ``User`` ou ``None``.
        """
        return User.objects.filter(email__iexact=email).first()

    def get_by_crm(self, crm: str) -> Optional[User]:
        """Busca usuário por CRM/identificação profissional (case-insensitive).

        Args:
            crm: Registro profissional a ser pesquisado.

        Returns:
            Instância de ``User`` ou ``None``.
        """
        return User.objects.filter(crm__iexact=crm).first()

    def get_by_identifier(self, identifier: str) -> Optional[User]:
        """Busca usuário por e-mail ou CRM — usado no fluxo de login.

        Tenta primeiro por e-mail; se não encontrar, tenta por CRM.

        Args:
            identifier: E-mail ou CRM do usuário.

        Returns:
            Instância de ``User`` ou ``None``.
        """
        user = self.get_by_email(identifier)
        if user is None:
            user = self.get_by_crm(identifier)
        return user

    def get_all_active(self) -> QuerySet[User]:
        """Retorna todos os usuários com ``is_active=True``.

        Returns:
            QuerySet de ``User`` ativos.
        """
        return User.objects.filter(is_active=True)

    def get_active_physicians(self) -> QuerySet[User]:
        """Retorna usuários ativos com papel ``medico`` ou ``tecnico``.

        Usado pelo endpoint de autocomplete do frontend para popular
        o campo "Médico Solicitante".

        Returns:
            QuerySet de ``User`` ordenado por nome.
        """
        return User.objects.filter(
            is_active=True,
            role__in=["medico", "tecnico"],
        ).order_by("first_name", "last_name")

    def create(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        crm: Optional[str] = None,
        role: str = "medico",
        is_active: bool = False,
    ) -> User:
        """Cria e persiste um novo usuário com senha criptografada.

        Args:
            username: Nome de usuário único.
            email: Endereço de e-mail único.
            password: Senha em texto plano (será hasheada com ``make_password``).
            first_name: Primeiro nome. Padrão: ``""``.
            last_name: Sobrenome. Padrão: ``""``.
            crm: Registro profissional. Padrão: ``None``.
            role: Papel do usuário (ver ``UserRole``). Padrão: ``"medico"``.
            is_active: Se a conta está ativa. Padrão: ``False`` (pendente).

        Returns:
            Instância de ``User`` recém-criada e salva.
        """
        user = User(
            username=username,
            email=email,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            crm=crm,
            role=role,
            is_active=is_active,
        )
        user.save()
        return user

    def update(self, user: User, **fields: object) -> User:
        """Atualiza campos específicos de um usuário e persiste.

        Usa ``save(update_fields=...)`` para emitir UPDATE seletivo no banco.

        Args:
            user: Instância de ``User`` a ser atualizada.
            **fields: Pares ``campo=valor`` a atualizar.

        Returns:
            Instância de ``User`` atualizada.
        """
        for attr, value in fields.items():
            setattr(user, attr, value)
        user.save(update_fields=list(fields.keys()))
        return user

    def activate(self, user: User) -> User:
        """Ativa a conta do usuário (aprovação pelo administrador).

        Args:
            user: Instância de ``User`` a ser ativada.

        Returns:
            Instância de ``User`` com ``is_active=True``.
        """
        return self.update(user, is_active=True)
