from typing import Optional

from django.contrib.auth.hashers import make_password
from django.db.models import QuerySet

from .models import User


class UserRepository:
    """
    Encapsulates all database operations for the User model.
    Views and services should never call User.objects directly.
    """

    def get_by_id(self, user_id: int) -> Optional[User]:
        return User.objects.filter(pk=user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return User.objects.filter(email__iexact=email).first()

    def get_by_crm(self, crm: str) -> Optional[User]:
        return User.objects.filter(crm__iexact=crm).first()

    def get_by_identifier(self, identifier: str) -> Optional[User]:
        """Returns user matching either email or CRM (used for login)."""
        user = self.get_by_email(identifier)
        if user is None:
            user = self.get_by_crm(identifier)
        return user

    def get_all_active(self) -> QuerySet[User]:
        return User.objects.filter(is_active=True)

    def get_active_physicians(self) -> QuerySet[User]:
        """Returns active users with role medico or tecnico (used for physician autocomplete)."""
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
        for attr, value in fields.items():
            setattr(user, attr, value)
        user.save(update_fields=list(fields.keys()))
        return user

    def activate(self, user: User) -> User:
        return self.update(user, is_active=True)
