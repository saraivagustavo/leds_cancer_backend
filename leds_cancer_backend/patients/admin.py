from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("name", "cpf", "birth_date", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "cpf", "email")
    ordering = ("name",)
