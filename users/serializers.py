from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.models import Doctor, Patient

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'patronymic',
            'role',
        )


class DoctorSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Doctor
        fields = ('id', 'user', 'specialization')


class PatientSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    phone = serializers.CharField(source='phone.as_e164')

    class Meta:
        model = Patient
        fields = ('id', 'user', 'phone', 'email')
