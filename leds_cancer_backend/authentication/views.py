from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet

from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True, required=False)

    class Meta:
        model = Doctor
        exclude = ("password", "is_superuser", "is_staff", "is_active", "date_joined")

    def get_full_name(self, obj: Doctor) -> str | None:
        if not obj.first_name and not obj.last_name:
            return None
        return f"{obj.first_name} {obj.last_name}".strip()


class DoctorViewSet(ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
