from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Consultation
from .permissions import (
    IsAdminOrDoctor,
    IsConsultationOwnerOrAdmin,
    IsDoctorOrPatient,
)
from .serializers import ConsultationSerializer


class ConsultationViewSet(viewsets.ModelViewSet):
    """ViewSet для консультации."""

    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    search_fields = (
        'doctor__user__first_name',
        'doctor__user__last_name',
        'doctor__user__patronymic',
        'patient__user__first_name',
        'patient__user__last_name',
        'patient__user__patronymic',
    )
    filterset_fields = ('status',)
    ordering_fields = ('created_at',)
    ordering = ('-created_at',)

    def get_queryset(self):
        qs = Consultation.objects.all()

        if self.action == 'list':
            user = self.request.user
            if user.role == user.UserRole.DOCTOR.value and hasattr(
                user, 'doctor_profile'
            ):
                qs = qs.filter(doctor=user.doctor_profile)
            elif user.role == user.UserRole.PATIENT.value and hasattr(
                user, 'patient_profile'
            ):
                qs = qs.filter(patient=user.patient_profile)
        return qs

    def get_permissions(self):
        """Разрешения в зависимости от действия."""

        if self.action == 'list':
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            self.permission_classes = [IsAuthenticated, IsAdminOrDoctor]
        elif self.action == 'retrieve':
            self.permission_classes = [IsAuthenticated, IsDoctorOrPatient]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [
                IsAuthenticated,
                IsConsultationOwnerOrAdmin,
            ]
        else:
            self.permission_classes = [IsAuthenticated]

        return super().get_permissions()

    def perform_create(self, serializer):
        """Создание новой консультации."""

        serializer.save()

    @action(
        detail=True,
        methods=['patch'],
        permission_classes=[IsAuthenticated, IsAdminOrDoctor],
    )
    def change_status(self, request, pk=None):
        """Метод для смены статуса консультации."""

        consultation = self.get_object()
        new_status = request.data.get('status')
        valid_statuses = [choice[0] for choice in Consultation.Status.choices]

        if new_status not in valid_statuses:
            return Response({'detail': 'Недопустимый статус.'}, status=400)

        consultation.status = new_status
        consultation.save()
        serializer = self.get_serializer(consultation)

        return Response(serializer.data)
