from rest_framework import serializers

from .models import Clinic


class ClinicSerializer(serializers.ModelSerializer):
    """Сериализатор для клиники."""

    class Meta:
        model = Clinic
        fields = ('id', 'name', 'legal_address', 'physical_address')
