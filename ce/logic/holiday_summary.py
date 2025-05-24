from decimal import Decimal, ROUND_HALF_UP
from ce.models import HolidaySummary, HolidayEvent  # Make sure these don't re-import logic
from django.db.models import Sum


def calculate_holiday_summary(participant, project):
    """
    Creates or updates a HolidaySummary record for a given participant and project.

    This calculates:
    - Total holiday hours entitled (based on weeks active in the project)
    - Sick leave entitlement (certified and uncertified)

    The summary is either created or updated depending on existence.
    """

    # ----------- Step 1: Determine participant's number of active weeks in the project ------------------ #

    start = max(participant.scheme_start_date, project.start_date)
    end = min(participant.scheme_finish_date, project.end_date)

    if start > end:
        # No overlap → no entitlement
        weeks_active = 0
    else:
        days_active = (end - start).days
        weeks_active = days_active // 7

    # ------------------------ Step 2: Calculate holiday entitlements ------------------------------------ #

    hol_hours_entitled = Decimal(weeks_active) * Decimal('1.56')

    # ------------------------ Step 3: Calculate sick leave entitlements --------------------------------- #

    def prorated_sick_entitlements(weeks):
        full_cert = Decimal('56.0')
        full_uncert = Decimal('8.0')
        total_weeks = Decimal('52')

        cert_hours = (full_cert * Decimal(weeks_active) / total_weeks).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        uncert_hours = (full_uncert * Decimal(weeks_active) / total_weeks).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return cert_hours, uncert_hours

    sick_cert_entitled, sick_uncert_entitled = prorated_sick_entitlements(weeks_active)

    # ------------------------- Step 4: Get or create the summary ---------------------------------------- #

    summary, created = HolidaySummary.objects.get_or_create(
        participant=participant,
        project=project,
        defaults={
            'hours_entitled': hol_hours_entitled,
            'hours_taken': Decimal('0.00'),
            'hours_in_lieu': Decimal('0.00'),
            'sick_cert_hours_entitled': sick_cert_entitled,
            'sick_cert_hours_taken': Decimal('0.00'),
            'sick_uncert_hours_entitled': sick_uncert_entitled,
            'sick_uncert_hours_taken': Decimal('0.00'),
        }
    )

    # --------------------- Step 4: Update if already exists ------------------------------------------------ #
    if not created:
        summary.hours_entitled = hol_hours_entitled
        summary.sick_cert_hours_entitled = sick_cert_entitled
        summary.sick_uncert_hours_entitled = sick_uncert_entitled
        summary.save()

    return summary
