from django.contrib import admin

from .models import Consultation

EMPTY_VALUE = '-ПУСТО-'


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    """Админка для консультации."""

    list_display = (
        'id',
        'created_at',
        'start_time',
        'end_time',
        'status',
        'doctor',
        'patient',
    )
    search_fields = (
        'doctor__user__first_name',
        'doctor__user__last_name',
        'patient__user__first_name',
        'patient__user__last_name',
    )
    list_filter = ('status', 'doctor', 'patient', 'created_at')
    ordering = ('-created_at',)
    empty_value_display = EMPTY_VALUE
