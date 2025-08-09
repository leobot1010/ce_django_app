from django.test import TestCase, Client
from django.urls import reverse
from ce.models import Participant, Scheme, Project
from datetime import date
from django.contrib.auth.models import User


class AddParticipantFormTest(TestCase):

    def setUp(self):
        # First, create a Scheme
        self.scheme = Scheme.objects.create(
            name="Test Scheme",
            gov_code="TS001",
            county="Kerry",
            address="Main St"
        )

        # Then, create a Project linked to that Scheme
        self.project = Project.objects.create(
            scheme=self.scheme,  # ✅ Link it here
            number=20,
            start_date=date(2024, 10, 14),
            end_date=date(2025, 10, 13)
        )

        # Set current_project on Scheme
        self.scheme.current_project = self.project  # ✅ use the actual project object, not 1
        self.scheme.save()

        # Simulate session login
        self.client = Client()
        session = self.client.session
        session['scheme_id'] = self.scheme.id
        session.save()


    def test_add_participant_valid_data(self):
        response = self.client.post(reverse('add_participants'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'ppsn': '1234567A',
            'email': 'john@example.com',
            'phone': '012345678',
            'emerg_phone': '0876543210',
            'address': '123 Main St',
            'birth_date': '1990-01-01',
            'manual_start_date': '2022-01-01',
            'scheme_start_date': '2022-01-03',
            'bank_iban': 'IE29AIBK93115212345678',
        })

        # Ensure redirect or success
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "✅ Participant added successfully.")
        self.assertTrue(Participant.objects.filter(email='john@example.com').exists())
