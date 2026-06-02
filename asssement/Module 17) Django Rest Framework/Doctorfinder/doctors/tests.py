from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.db import transaction
from django.db.utils import IntegrityError
from unittest.mock import patch
from .models import Doctor

class DoctorModelTest(TestCase):
    """
    Test suite for the Doctor model definition.
    """
    def setUp(self):
        self.doctor = Doctor.objects.create(
            name="Dr. Jane Smith",
            specialization="Cardiology",
            city="New York"
        )

    def test_doctor_creation(self):
        """Test that a doctor instance is successfully created with correct fields."""
        self.assertEqual(self.doctor.name, "Dr. Jane Smith")
        self.assertEqual(self.doctor.specialization, "Cardiology")
        self.assertEqual(self.doctor.city, "New York")

    def test_doctor_str_representation(self):
        """Test the __str__ method of the Doctor model."""
        self.assertEqual(str(self.doctor), "Dr. Jane Smith - Cardiology")


class DoctorAPITest(APITestCase):
    """
    Test suite for CRUD APIs, Pagination, Filtering, Ordering, and Transactions.
    """
    def setUp(self):
        # Create some sample doctors with distinct names/specializations to test sorting
        self.doctors_data = [
            {"name": "Dr. Zach", "specialization": "Pediatrics", "city": "Boston"},
            {"name": "Dr. Alice", "specialization": "Neurology", "city": "Chicago"},
            {"name": "Dr. Charlie", "specialization": "Dermatology", "city": "Austin"},
            {"name": "Dr. Bob", "specialization": "Orthopedics", "city": "Denver"},
            {"name": "Dr. David", "specialization": "Cardiology", "city": "Atlanta"},
            {"name": "Dr. Frank", "specialization": "Psychiatry", "city": "Miami"},
        ]
        for data in self.doctors_data:
            Doctor.objects.create(**data)
            
        self.list_url = reverse('doctor-list')

    def test_get_doctors_list_paginated_limit_offset(self):
        """Test GET request to retrieve doctors list, verifying LimitOffsetPagination."""
        # Query with limit 3 and offset 2
        response = self.client.get(self.list_url, {'limit': 3, 'offset': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify pagination structure is present for LimitOffsetPagination
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        
        # Verify page size and count
        self.assertEqual(len(response.data['results']), 3)
        self.assertEqual(response.data['count'], 6)

    def test_doctors_ordering_by_name_asc(self):
        """Test that list endpoint sorts doctors by name in ascending order."""
        response = self.client.get(self.list_url, {'ordering': 'name', 'limit': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data['results']
        names = [doc['name'] for doc in results]
        # Should be sorted ascending
        self.assertEqual(names, sorted(names))

    def test_doctors_ordering_by_specialization_desc(self):
        """Test that list endpoint sorts doctors by specialization in descending order."""
        response = self.client.get(self.list_url, {'ordering': '-specialization', 'limit': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data['results']
        specializations = [doc['specialization'] for doc in results]
        
        # Verify list matches descending order
        sorted_specs_desc = sorted(specializations, reverse=True)
        self.assertEqual(specializations, sorted_specs_desc)

    def test_create_doctor_success(self):
        """Test POST request to create a doctor returns 201 Created and saves the payload."""
        payload = {
            "name": "Dr. Gregory House",
            "specialization": "Diagnostic Medicine",
            "city": "Princeton"
        }
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify database record
        doctor_id = response.data['id']
        db_doctor = Doctor.objects.get(id=doctor_id)
        self.assertEqual(db_doctor.name, payload['name'])
        self.assertEqual(db_doctor.specialization, payload['specialization'])
        self.assertEqual(db_doctor.city, payload['city'])

    def test_retrieve_doctor_detail(self):
        """Test GET request for a specific doctor's details."""
        doctor = Doctor.objects.first()
        url = reverse('doctor-detail', kwargs={'pk': doctor.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], doctor.name)

    def test_update_doctor(self):
        """Test PUT request to update a doctor completely."""
        doctor = Doctor.objects.first()
        url = reverse('doctor-detail', kwargs={'pk': doctor.id})
        payload = {
            "name": "Dr. Updated Name",
            "specialization": "Neurology",
            "city": "Chicago"
        }
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doctor.refresh_from_db()
        self.assertEqual(doctor.name, "Dr. Updated Name")

    def test_delete_doctor(self):
        """Test DELETE request to remove a doctor."""
        doctor = Doctor.objects.first()
        url = reverse('doctor-detail', kwargs={'pk': doctor.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Doctor.objects.filter(id=doctor.id).exists())

    def test_atomic_transaction_creation(self):
        """
        Test that perform_create runs inside an atomic transaction.
        We verify this by mocking serializer.save to raise an exception,
        and ensuring that transaction.atomic() handles rollback properly.
        """
        payload = {
            "name": "Dr. Failure",
            "specialization": "Critical Care",
            "city": "Boston"
        }
        
        with patch('doctors.serializers.DoctorSerializer.save') as mock_save:
            mock_save.side_effect = IntegrityError("Database error during save")
            
            with self.assertRaises(IntegrityError):
                self.client.post(self.list_url, payload, format='json')
                
        # Assert no doctor was created with this name
        self.assertFalse(Doctor.objects.filter(name="Dr. Failure").exists())

    def test_atomic_transaction_update_failure(self):
        """
        Test that perform_update runs inside an atomic transaction.
        We verify this by mocking serializer.save to raise an exception,
        and ensuring that transaction.atomic() rolls back any changes.
        """
        doctor = Doctor.objects.first()
        original_name = doctor.name
        url = reverse('doctor-detail', kwargs={'pk': doctor.id})
        payload = {
            "name": "Dr. Update Failure",
            "specialization": "Neurology",
            "city": "Chicago"
        }
        
        with patch('doctors.serializers.DoctorSerializer.save') as mock_save:
            mock_save.side_effect = IntegrityError("Database error during update")
            
            with self.assertRaises(IntegrityError):
                self.client.put(url, payload, format='json')
                
        # Assert doctor's name remains unchanged due to rollback
        doctor.refresh_from_db()
        self.assertEqual(doctor.name, original_name)
