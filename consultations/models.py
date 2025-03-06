from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()


class Consultation(models.Model):
    """Модель консультации на прием к врачу."""

    class Status(models.TextChoices):
        CONFIRMED = 'Confirmed', 'Подтверждена'
        WAITING = 'Waiting', 'Ожидает'
        STARTED = 'Started', 'Начата'
        FINISHED = 'Finished', 'Завершена'
        PAID = 'Paid', 'Оплачена'

    created_at = models.DateTimeField(
        'Дата создания консультации',
        auto_now_add=True,
        db_index=True,
    )
    start_time = models.DateTimeField('Время начала приема', db_index=True)
    end_time = models.DateTimeField('Время окончания приема')
    status = models.CharField(
        'Статус консультации',
        max_length=15,
        choices=Status.choices,
        default=Status.WAITING.value,
    )
    doctor = models.ForeignKey(
        'users.Doctor',
        verbose_name='Врач',
        on_delete=models.CASCADE,
        related_name='doctor_consultations',
    )
    patient = models.ForeignKey(
        'users.Patient',
        verbose_name='Пациент',
        on_delete=models.CASCADE,
        related_name='patient_consultations',
    )

    class Meta:
        verbose_name = 'Консультация'
        verbose_name_plural = 'Консультации'
        ordering = ('-created_at',)
        constraints = (
            models.UniqueConstraint(
                fields=['doctor', 'start_time'],
                name='unique_doctor_consultation_time',
            ),
        )

    def __str__(self):
        return f'Консультация {self.id} со статусом {self.status}'

    def clean(self):
        super().clean()

        if not self.doctor:
            raise ValidationError('Не выбран врач для консультации.')

        if not self.patient:
            raise ValidationError('Не выбран пациент для консультации.')

        if (
            self.start_time
            and self.end_time
            and self.start_time >= self.end_time
        ):
            raise ValidationError(
                'Время начала должно быть раньше времени окончания.'
            )

        if self.doctor.user == self.patient.user:
            raise ValidationError(
                'Доктор и пациент не могут быть одним и тем же человеком.'
            )
