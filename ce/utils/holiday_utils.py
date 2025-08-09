from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from ce.models import HolidaySummary


# ----------------------------------------------------------------------------- #
# ---------- Calculate the Participant's active weeks in the project ---------- #

def calculate_participant_active_weeks(start_date, finish_date, project_start, project_end):
    """
    Calculates how many full weeks a participant is active during the project period.
    """
    if finish_date is None:
        finish_date = start_date + timedelta(weeks=52) - timedelta(days=3)

    start_calc = max(start_date, project_start)
    finish_calc = min(finish_date, project_end)

    if start_calc > finish_calc:
        return 0

    return (finish_calc - start_calc).days // 7


# ----------------------------------------------------------------------------- #
# --------------- Calculate the Participant's Holiday Allowance --------------- #

def calculate_holiday_hours(weeks_active):
    """
    Calculates the hours holidays a participant is entitled to for a project period
    """
    return Decimal(weeks_active) * Decimal('1.56')


# ----------------------------------------------------------------------------- #
# ------------ Calculate the Participant's Sick Leave entitlements ------------ #

def prorated_sick_entitlements(weeks_active):
    """
    Calculates the sick entitlement hours for a participant for a project period
    """
    full_cert = Decimal('56.0')
    full_uncert = Decimal('8.0')
    total_weeks = Decimal('52')

    cert_hours = (full_cert * Decimal(weeks_active) / total_weeks).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    uncert_hours = (full_uncert * Decimal(weeks_active) / total_weeks).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return cert_hours, uncert_hours


# ---------------------------------------------------------------------------- #
# ---------- Create or Update Full Summary and Save to the Database ---------- #


def create_or_update_holiday_summary(participant, project):
    """
    Creates or updates the HolidaySummary for a given participant and project.
    """
    weeks_active = calculate_participant_active_weeks(
        participant.scheme_start_date,
        participant.scheme_finish_date,
        project.start_date,
        project.end_date
    )

    hol_hours_entitled = calculate_holiday_hours(weeks_active)
    sick_cert_entitled, sick_uncert_entitled = prorated_sick_entitlements(weeks_active)

    summary, created = HolidaySummary.objects.get_or_create(
        participant=participant,
        project=project,
        defaults={
            'hol_hours_entitled': hol_hours_entitled,
            'hol_hours_taken': Decimal('0.00'),
            'hol_hours_in_lieu': Decimal('0.00'),
            'sick_cert_hours_entitled': sick_cert_entitled,
            'sick_cert_hours_taken': Decimal('0.00'),
            'sick_uncert_hours_entitled': sick_uncert_entitled,
            'sick_uncert_hours_taken': Decimal('0.00'),
        }
    )

    if not created:
        summary.hol_hours_entitled = hol_hours_entitled
        summary.sick_cert_hours_entitled = sick_cert_entitled
        summary.sick_uncert_hours_entitled = sick_uncert_entitled
        summary.save()

    return summary


