from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from clinics.models import Clinic


class CustomUser(AbstractUser):
    """Кастомная модель для пользователя."""

    class UserRole(models.TextChoices):
        """Типы ролей для пользователя."""

        ADMIN = 'Admin', 'Админ'
        PATIENT = 'Patient', 'Пациент'
        DOCTOR = 'Doctor', 'Врач'

    role = models.CharField(
        'Роль',
        max_length=15,
        choices=UserRole.choices,
        default=UserRole.PATIENT.value,
    )
    patronymic = models.CharField(
        'Отчество',
        max_length=50,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Doctor(models.Model):
    """Модель для врача."""

    user = models.OneToOneField(
        CustomUser,
        verbose_name='Врач',
        on_delete=models.CASCADE,
        related_name='doctor_profile',
    )
    specialization = models.CharField(
        'Специализация',
        max_length=50,
    )
    clinics = models.ManyToManyField(
        Clinic,
        verbose_name='Клиники',
        related_name='clinic_doctors',
    )

    class Meta:
        verbose_name = 'Врач'
        verbose_name_plural = 'Врачи'
        ordering = ('user__last_name', 'user__first_name')

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def clean(self):
        if self.user.role != CustomUser.UserRole.DOCTOR.value:
            raise ValidationError('Пользователь должен иметь роль "Врач".')


class Patient(models.Model):
    """Модель для пациента."""

    user = models.OneToOneField(
        CustomUser,
        verbose_name='Пациент',
        on_delete=models.CASCADE,
        related_name='patient_profile',
    )
    phone = PhoneNumberField(
        'Номер телефона',
        region='RU',
        unique=True,
    )
    email = models.EmailField('E-mail', unique=True, db_index=True)

    class Meta:
        verbose_name = 'Пациент'
        verbose_name_plural = 'Пациенты'
        ordering = ('user__last_name', 'user__first_name')

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def clean(self):
        if self.user.role != CustomUser.UserRole.PATIENT.value:
            raise ValidationError('Пользователь должен иметь роль "Пациент".')
