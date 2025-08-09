from datetime import date
from django.test import TestCase
from ce.utils.project_utils import (
    calculate_project_dates,
    validate_participant_start_date,
)


class ProjectUtilsTests(TestCase):
    def test_calculate_project_dates(self):
        start = date(2024, 10, 14)
        end, next_start, next_end = calculate_project_dates(start)
        self.assertEqual(end, date(2025, 10, 10))
        self.assertEqual(next_start, date(2025, 10, 13))
        self.assertEqual(next_end, date(2026, 10, 9))

    def test_validate_participant_start_date_valid(self):
        # Should print ✓ valid
        start = date(2024, 10, 14)
        validate_participant_start_date(start)  # no error means valid
