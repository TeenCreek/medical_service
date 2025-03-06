from rest_framework import serializers

from users.models import Doctor, Patient

from .models import Consultation


class ConsultationSerializer(serializers.ModelSerializer):
    """Сериализатор для консультаций."""

    doctor = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), required=True
    )
    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(), required=True
    )
    status = serializers.ChoiceField(choices=Consultation.Status.choices)

    class Meta:
        model = Consultation
        fields = (
            'id',
            'created_at',
            'start_time',
            'end_time',
            'status',
            'doctor',
            'patient',
        )

    def validate(self, data):
        """Дополнительная проверка валидности."""

        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError(
                'Время начала должно быть раньше времени окончания.'
            )

        if data['doctor'].user == data['patient'].user:
            raise serializers.ValidationError(
                'Доктор и пациент не могут быть одним и тем же человеком.'
            )

        return data
