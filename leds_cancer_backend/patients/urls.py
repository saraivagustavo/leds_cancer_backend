from typing import Any

from django.urls import path

from .views import PatientDetailView, PatientListCreateView

urlpatterns: list[Any] = [
    path("patients/", PatientListCreateView.as_view(), name="patient-list-create"),
    path("patients/<int:pk>/", PatientDetailView.as_view(), name="patient-detail"),
]
