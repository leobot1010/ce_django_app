from datetime import date
from decimal import Decimal
from django.test import TestCase
from ce.utils.holiday_utils import (
    calculate_participant_active_weeks,
    calculate_holiday_hours,
    generate_participant_holiday_summary,
)


class HolidayUtilsTests(TestCase):
    def test_active_weeks_custom_end(self):
        start = date(2024, 10, 14)
        end = date(2024, 12, 16)
        weeks = calculate_participant_active_weeks(start, end)
        self.assertEqual(weeks, 10)

    def test_active_weeks_default_end(self):
        start = date(2024, 10, 14)
        weeks = calculate_participant_active_weeks(start)
        self.assertEqual(weeks, 52)

    def test_calculate_holiday_hours(self):
        hours = calculate_holiday_hours(10)
        self.assertEqual(hours, Decimal('15.60'))

    def test_generate_holiday_summary(self):
        start = date(2024, 10, 14)
        end = date(2024, 12, 16)
        summary = generate_participant_holiday_summary(start, end)
        self.assertEqual(summary["weeks_active"], 10)
        self.assertEqual(summary["holiday_hours"], Decimal('15.60'))
