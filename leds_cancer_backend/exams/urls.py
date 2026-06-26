from typing import Any

from django.urls import path

from .views import DashboardStatsView, ExamDetailView, ExamListCreateView, RecentExamsView

urlpatterns: list[Any] = [
    # Dashboard
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    # Exams
    path("exams/", ExamListCreateView.as_view(), name="exam-list-create"),
    path("exams/recent/", RecentExamsView.as_view(), name="exam-recent"),
    path("exams/<int:pk>/", ExamDetailView.as_view(), name="exam-detail"),
]
