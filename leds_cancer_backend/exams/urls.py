from typing import Any

from django.urls import path

from .views import (
    DashboardStatsView,
    ExamDetailView,
    ExamImageDownloadView,
    ExamImageTokenView,
    ExamListCreateView,
    RecentExamsView,
)

urlpatterns: list[Any] = [
    # Dashboard
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    # Exams
    path("exams/", ExamListCreateView.as_view(), name="exam-list-create"),
    path("exams/recent/", RecentExamsView.as_view(), name="exam-recent"),
    path("exams/<int:pk>/", ExamDetailView.as_view(), name="exam-detail"),
    # Image access
    path("exams/<int:pk>/image-token/", ExamImageTokenView.as_view(), name="exam-image-token"),
    path("exams/<int:pk>/image/", ExamImageDownloadView.as_view(), name="exam-image-download"),
]
