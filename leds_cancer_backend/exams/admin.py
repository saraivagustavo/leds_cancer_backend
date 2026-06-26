from django.contrib import admin

from .models import Exam


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("patient", "exam_type", "exam_date", "status", "radiologist", "created_at")
    list_filter = ("status", "technique", "breast_side")
    search_fields = ("patient__name", "requesting_physician", "radiologist__username")
    autocomplete_fields = ("patient",)
    ordering = ("-exam_date",)
    raw_id_fields = ("radiologist",)
