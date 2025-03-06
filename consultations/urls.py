from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ConsultationViewSet

app_name = 'consultations'

v1_router = DefaultRouter()
v1_router.register(
    'consultations', ConsultationViewSet, basename='consultations'
)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]
