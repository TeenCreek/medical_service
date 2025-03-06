from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from consultations.models import Consultation
from users.models import CustomUser, Doctor, Patient


@pytest.fixture
def api_client():
    """Возвращает экземпляр APIClient."""

    return APIClient()


@pytest.fixture
def admin_user(db, django_user_model):
    """Создаёт и возвращает пользователя-администратора."""

    user = django_user_model.objects.create_user(
        username='admin',
        password='password',
        role=CustomUser.UserRole.ADMIN.value,
        first_name='Admin',
        last_name='User',
    )
    return user


@pytest.fixture
def doctor_user(db, django_user_model):
    """Создаёт и возвращает пользователя-врача с профилем Doctor."""

    user = django_user_model.objects.create_user(
        username='doctor',
        password='password',
        role=CustomUser.UserRole.DOCTOR.value,
        first_name='John',
        last_name='Doe',
    )
    doctor = Doctor.objects.create(user=user, specialization="Cardiology")
    return doctor


@pytest.fixture
def other_doctor(db, django_user_model):
    """Создаёт и возвращает другого пользователя-врача с профилем Doctor."""

    user = django_user_model.objects.create_user(
        username='doctor2',
        password='password',
        role=CustomUser.UserRole.DOCTOR.value,
        first_name='Alice',
        last_name='Smith',
    )
    doctor = Doctor.objects.create(user=user, specialization="Neurology")
    return doctor


@pytest.fixture
def patient_user(db, django_user_model):
    """Создаёт и возвращает пользователя-пациента с профилем Patient."""

    user = django_user_model.objects.create_user(
        username='patient',
        password='password',
        role=CustomUser.UserRole.PATIENT.value,
        first_name='Jane',
        last_name='Doe',
    )
    patient = Patient.objects.create(
        user=user, phone='+71234567890', email='jane@example.com'
    )
    return patient


@pytest.fixture
def other_patient(db, django_user_model):
    """
    Создаёт и возвращает другого пользователя-пациента с профилем Patient.
    """

    user = django_user_model.objects.create_user(
        username='patient2',
        password='password',
        role=CustomUser.UserRole.PATIENT.value,
        first_name='Bob',
        last_name='Brown',
    )
    patient = Patient.objects.create(
        user=user, phone='+79876543210', email='bob@example.com'
    )
    return patient


@pytest.fixture
def consultation_payload(doctor_user, patient_user):
    """Возвращает словарь с данными для создания Consultation."""

    now = timezone.now() + timedelta(hours=1)
    return {
        'start_time': now.isoformat(),
        'end_time': (now + timedelta(hours=1)).isoformat(),
        'status': 'Waiting',
        'doctor': doctor_user.pk,
        'patient': patient_user.pk,
    }


@pytest.mark.django_db
def test_token_obtain(api_client, admin_user):
    """
    Проверяет, что при запросе токена возвращаются access и refresh токены.
    """

    url = reverse('token_obtain_pair')
    response = api_client.post(
        url,
        data={'username': admin_user.username, 'password': 'password'},
        format='json',
    )
    assert response.status_code == 200, response.data
    data = response.json()
    assert 'access' in data
    assert 'refresh' in data


@pytest.mark.django_db
def test_token_refresh(api_client, admin_user):
    """Проверяет, что при обновлении токена возвращается новый access токен."""

    token_url = reverse('token_obtain_pair')
    response = api_client.post(
        token_url,
        data={'username': admin_user.username, 'password': 'password'},
        format='json',
    )
    tokens = response.json()
    refresh_url = reverse('token_refresh')
    response_refresh = api_client.post(
        refresh_url, data={'refresh': tokens['refresh']}, format='json'
    )
    assert response_refresh.status_code == 200
    data_refresh = response_refresh.json()
    assert 'access' in data_refresh


@pytest.mark.django_db
def test_create_consultation_as_doctor(
    api_client, doctor_user, patient_user, consultation_payload
):
    """Проверяет, что врач может создать Consultation."""

    url = reverse('consultations:consultations-list')
    api_client.force_authenticate(user=doctor_user.user)
    response = api_client.post(url, data=consultation_payload, format='json')
    assert response.status_code == 201, response.data
    data = response.json()
    assert data['doctor'] == doctor_user.pk
    assert data['patient'] == patient_user.pk


@pytest.mark.django_db
def test_create_consultation_as_patient(
    api_client, patient_user, consultation_payload
):
    """Проверяет, что пациенту запрещено создавать Consultation."""

    url = reverse('consultations:consultations-list')
    api_client.force_authenticate(user=patient_user.user)
    response = api_client.post(url, data=consultation_payload, format='json')
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_consultation_invalid_times(
    api_client, doctor_user, patient_user, consultation_payload
):
    """
    Проверяет валидацию: время начала должно быть раньше времени окончания.
    """

    now = timezone.now() + timedelta(hours=1)
    consultation_payload['start_time'] = now.isoformat()
    consultation_payload['end_time'] = now.isoformat()
    url = reverse('consultations:consultations-list')
    api_client.force_authenticate(user=doctor_user.user)
    response = api_client.post(url, data=consultation_payload, format='json')
    assert response.status_code == 400
    assert 'Время начала должно быть раньше времени окончания.' in str(
        response.data
    )


@pytest.mark.django_db
def test_create_consultation_same_doctor_and_patient(
    api_client, doctor_user, consultation_payload
):
    """
    Проверяет валидацию: доктор и пациент
    не могут быть одним и тем же человеком.
    """
    from users.models import Patient

    patient_same = Patient.objects.create(
        user=doctor_user.user, phone='+70000000000', email='dup@example.com'
    )
    consultation_payload['patient'] = patient_same.pk
    url = reverse('consultations:consultations-list')
    api_client.force_authenticate(user=doctor_user.user)
    response = api_client.post(url, data=consultation_payload, format='json')
    assert response.status_code == 400
    assert 'Доктор и пациент не могут быть одним и тем же человеком.' in str(
        response.data
    )


@pytest.mark.django_db
def test_list_consultations_as_doctor(
    api_client, doctor_user, other_doctor, patient_user, other_patient
):
    """Проверяет, что врач видит в списке только свои Consultation."""

    now = timezone.now() + timedelta(hours=1)
    consultation1 = Consultation.objects.create(
        start_time=now,
        end_time=now + timedelta(hours=1),
        status='Waiting',
        doctor=doctor_user,
        patient=patient_user,
    )
    consultation2 = Consultation.objects.create(
        start_time=now + timedelta(days=1),
        end_time=now + timedelta(days=1, hours=1),
        status='Waiting',
        doctor=other_doctor,
        patient=other_patient,
    )
    url = reverse('consultations:consultations-list')
    api_client.force_authenticate(user=doctor_user.user)
    response = api_client.get(url, format='json')
    assert response.status_code == 200
    data = response.json()
    assert any(item['id'] == consultation1.pk for item in data)
    assert not any(item['id'] == consultation2.pk for item in data)


@pytest.mark.django_db
def test_list_consultations_as_patient(
    api_client, doctor_user, patient_user, other_patient
):
    """Проверяет, что пациент видит в списке только свои Consultation."""

    now = timezone.now() + timedelta(hours=1)
    consultation1 = Consultation.objects.create(
        start_time=now,
        end_time=now + timedelta(hours=1),
        status='Waiting',
        doctor=doctor_user,
        patient=patient_user,
    )
    consultation2 = Consultation.objects.create(
        start_time=now + timedelta(days=1),
        end_time=now + timedelta(days=1, hours=1),
        status='Waiting',
        doctor=doctor_user,
        patient=other_patient,
    )
    url = reverse('consultations:consultations-list')
    api_client.force_authenticate(user=patient_user.user)
    response = api_client.get(url, format='json')
    assert response.status_code == 200
    data = response.json()
    assert any(item['id'] == consultation1.pk for item in data)
    assert not any(item['id'] == consultation2.pk for item in data)


@pytest.mark.django_db
def test_retrieve_consultation(api_client, doctor_user, patient_user):
    """
    Проверяет, что детали Consultation доступны
    как для врача, так и для пациента.
    """

    now = timezone.now() + timedelta(hours=1)
    consultation = Consultation.objects.create(
        start_time=now,
        end_time=now + timedelta(hours=1),
        status='Waiting',
        doctor=doctor_user,
        patient=patient_user,
    )
    url = reverse('consultations:consultations-detail', args=[consultation.pk])
    api_client.force_authenticate(user=doctor_user.user)
    response = api_client.get(url, format='json')
    assert response.status_code == 200
    api_client.force_authenticate(user=patient_user.user)
    response = api_client.get(url, format='json')
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_consultation_as_doctor(api_client, doctor_user, patient_user):
    """Проверяет, что врач-владелец может обновить Consultation."""

    now = timezone.now() + timedelta(hours=1)
    consultation = Consultation.objects.create(
        start_time=now,
        end_time=now + timedelta(hours=1),
        status='Waiting',
        doctor=doctor_user,
        patient=patient_user,
    )
    url = reverse('consultations:consultations-detail', args=[consultation.pk])
    api_client.force_authenticate(user=doctor_user.user)
    update_data = {
        'start_time': (now + timedelta(minutes=15)).isoformat(),
        'end_time': (now + timedelta(hours=1, minutes=15)).isoformat(),
        'status': 'Confirmed',
        'doctor': doctor_user.pk,
        'patient': patient_user.pk,
    }
    response = api_client.put(url, data=update_data, format='json')
    assert response.status_code == 200
    updated = response.json()
    assert updated['status'] == 'Confirmed'


@pytest.mark.django_db
def test_delete_consultation_as_admin(
    api_client, admin_user, doctor_user, patient_user
):
    """Проверяет, что администратор может удалить Consultation."""

    now = timezone.now() + timedelta(hours=1)
    consultation = Consultation.objects.create(
        start_time=now,
        end_time=now + timedelta(hours=1),
        status='Waiting',
        doctor=doctor_user,
        patient=patient_user,
    )
    url = reverse('consultations:consultations-detail', args=[consultation.pk])
    api_client.force_authenticate(user=admin_user)
    response = api_client.delete(url)
    assert response.status_code == 204
    with pytest.raises(Consultation.DoesNotExist):
        Consultation.objects.get(pk=consultation.pk)


@pytest.mark.django_db
def test_delete_consultation_as_non_owner(
    api_client, doctor_user, other_doctor, patient_user
):
    """
    Проверяет, что врач, не являющийся владельцем,
    не может удалить Consultation.
    """

    now = timezone.now() + timedelta(hours=1)
    consultation = Consultation.objects.create(
        start_time=now,
        end_time=now + timedelta(hours=1),
        status='Waiting',
        doctor=doctor_user,
        patient=patient_user,
    )
    url = reverse('consultations:consultations-detail', args=[consultation.pk])
    api_client.force_authenticate(user=other_doctor.user)
    response = api_client.delete(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_change_status(api_client, doctor_user, patient_user):
    """Проверяет изменение статуса Consultation через кастомный action."""

    now = timezone.now() + timedelta(hours=1)
    consultation = Consultation.objects.create(
        start_time=now,
        end_time=now + timedelta(hours=1),
        status='Waiting',
        doctor=doctor_user,
        patient=patient_user,
    )
    url = reverse(
        'consultations:consultations-change-status', args=[consultation.pk]
    )
    api_client.force_authenticate(user=doctor_user.user)
    response = api_client.patch(
        url, data={'status': 'Confirmed'}, format='json'
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated['status'] == 'Confirmed'
    response_invalid = api_client.patch(
        url, data={'status': 'InvalidStatus'}, format='json'
    )
    assert response_invalid.status_code == 400


@pytest.mark.django_db
def test_search_filter_ordering(
    api_client,
    admin_user,
    doctor_user,
    patient_user,
    other_doctor,
    other_patient,
):
    """
    Проверяет работу поиска, фильтрации и сортировки в списке Consultation.
    """

    now = timezone.now() + timedelta(hours=1)
    consultation1 = Consultation.objects.create(
        start_time=now,
        end_time=now + timedelta(hours=1),
        status='Waiting',
        doctor=doctor_user,
        patient=patient_user,
    )
    consultation2 = Consultation.objects.create(
        start_time=now + timedelta(days=1),
        end_time=now + timedelta(days=1, hours=1),
        status='Confirmed',
        doctor=other_doctor,
        patient=other_patient,
    )
    url = reverse('consultations:consultations-list')
    api_client.force_authenticate(user=admin_user)
    response_search = api_client.get(url, {'search': 'Alice'}, format='json')
    assert response_search.status_code == 200
    data_search = response_search.json()
    assert any(item['id'] == consultation2.pk for item in data_search)
    response_filter = api_client.get(
        url, {'status': 'Confirmed'}, format='json'
    )
    assert response_filter.status_code == 200
    data_filter = response_filter.json()
    assert all(item['status'] == 'Confirmed' for item in data_filter)
    response_order = api_client.get(
        url, {'ordering': 'created_at'}, format='json'
    )
    assert response_order.status_code == 200
    data_order = response_order.json()
    created_dates = [item['created_at'] for item in data_order]
    assert created_dates == sorted(created_dates)
