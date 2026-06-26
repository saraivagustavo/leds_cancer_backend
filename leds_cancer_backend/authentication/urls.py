from typing import Any

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import CustomTokenObtainPairView, MeView, RegisterView, UpdatePasswordView, UpdateProfileView

urlpatterns: list[Any] = [
    path("auth/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("auth/me/update/", UpdateProfileView.as_view(), name="me-update"),
    path("auth/me/password/", UpdatePasswordView.as_view(), name="me-password"),
]
