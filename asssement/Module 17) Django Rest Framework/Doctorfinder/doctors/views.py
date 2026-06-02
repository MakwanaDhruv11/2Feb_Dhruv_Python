from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.filters import OrderingFilter
from django.db import transaction
from .models import Doctor
from .serializers import DoctorSerializer

class StandardLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 5
    max_limit = 100

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    pagination_class = StandardLimitOffsetPagination
    
    # Configure filtering and ordering
    filter_backends = [OrderingFilter]
    ordering_fields = ['name', 'specialization', 'city']
    ordering = ['id']  # Default ordering

    def perform_create(self, serializer):
        # Wrap creation in an atomic transaction to prevent orphan or partial data commits
        with transaction.atomic():
            serializer.save()

    def perform_update(self, serializer):
        # Wrap update in an atomic transaction to ensure profile update safety
        with transaction.atomic():
            serializer.save()

    def perform_destroy(self, instance):
        # Wrap deletion in an atomic transaction for complete database consistency
        with transaction.atomic():
            instance.delete()
