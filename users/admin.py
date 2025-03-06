from django.contrib import admin

from .models import CustomUser, Doctor, Patient

EMPTY_VALUE = '-ПУСТО-'


# Регистрация кастомного пользователя
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'role',
        'email',
        'is_staff',
        'is_active',
    )
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    empty_value_display = EMPTY_VALUE


# Регистрация врача
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'specialization',
    )
    search_fields = ('user__first_name', 'user__last_name', 'specialization')
    list_filter = ('specialization',)
    ordering = ('user__last_name', 'user__first_name')
    empty_value_display = EMPTY_VALUE


# Регистрация пациента
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'email')
    search_fields = ('user__first_name', 'user__last_name', 'phone', 'email')
    ordering = ('user__last_name', 'user__first_name')
    empty_value_display = EMPTY_VALUE
