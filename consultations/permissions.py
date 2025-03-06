from rest_framework.permissions import BasePermission

from users.models import CustomUser


class IsAdmin(BasePermission):
    """Разрешение, доступное только администратору."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == CustomUser.UserRole.ADMIN.value
        )


class IsDoctor(BasePermission):
    """Разрешение, доступное только доктору."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == CustomUser.UserRole.DOCTOR.value
        )


class IsPatient(BasePermission):
    """Разрешение, доступное только пациенту."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == CustomUser.UserRole.PATIENT.value
        )


class IsAdminOrDoctor(BasePermission):
    """
    Комбинированное разрешение: доступно, если пользователь - админ или доктор.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            CustomUser.UserRole.ADMIN.value,
            CustomUser.UserRole.DOCTOR.value,
        )


class IsDoctorOrPatient(BasePermission):
    """
    Комбинированное разрешение:
    доступно, если пользователь - доктор или пациент.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            CustomUser.UserRole.DOCTOR.value,
            CustomUser.UserRole.PATIENT.value,
        )


class IsConsultationOwnerOrAdmin(BasePermission):
    """
    Разрешение к доступу к объекту консультации
    для администратора и врача.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role == CustomUser.UserRole.ADMIN.value:
            return True

        if request.user.role == CustomUser.UserRole.DOCTOR.value and hasattr(
            request.user, 'doctor_profile'
        ):
            return obj.doctor == request.user.doctor_profile

        return False
