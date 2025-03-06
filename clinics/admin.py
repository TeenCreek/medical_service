from django.contrib import admin

from .models import Clinic

EMPTY_VALUE = '-ПУСТО-'


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    """Админка для клиники."""

    list_display = ('name', 'legal_address', 'physical_address')
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('name',)
    empty_value_display = EMPTY_VALUE
