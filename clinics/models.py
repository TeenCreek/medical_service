from django.db import models


class Clinic(models.Model):
    """Модель для клиники."""

    name = models.CharField('Название', max_length=250)
    legal_address = models.CharField('Юридический адрес', max_length=250)
    physical_address = models.CharField('Физический адрес', max_length=250)

    class Meta:
        verbose_name = 'Клиника'
        verbose_name_plural = 'Клиники'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=['name', 'legal_address', 'physical_address'],
                name='unique_clinic_address',
            ),
        )

    def __str__(self):
        return self.name
