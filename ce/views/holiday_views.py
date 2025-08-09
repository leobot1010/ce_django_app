from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from ce.models import HolidaySummary, HolidayEvent, Scheme, Participant
from django.db.models import Sum, Q, F, Value
from django.db.models.functions import Coalesce
from ce.utils.scheme_utils import get_current_scheme


@login_required
def holiday_summary(request):
    # Get current scheme from log-in session
    scheme = get_current_scheme(request)
    current_scheme = Scheme.objects.get(id=scheme)

    # Get current project
    current_project = current_scheme.current_project

    # Parameters that filter by department and search
    dept_id = request.GET.get('department')
    search_query = request.GET.get('search')

    # Base queryset
    participants = Participant.objects.select_related('department').filter(scheme=current_scheme)

    # Apply filters if provided
    if dept_id:
        participants = participants.filter(department_id=dept_id)
    if search_query:
        participants = participants.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    # Get holiday summaries for these participant in this project
    summaries = HolidaySummary.objects.filter(
        participant__in=participants,
        project=current_project
    )

    # Map summaries to participants by ID
    summary_map = {s.participant_id: s for s in summaries}

    # Annotate totals from HolidayEvent records
    participants = participants.annotate(
        holidays_taken=Coalesce(
            Sum('holidays__hours', filter=Q(holidays__type='take_hours')), Value(0)),

        holidays_in_lieu=Coalesce(
            Sum('holidays__hours', filter=Q(holidays__type='add_hours')), Value(0)),

        sick_certified_taken=Coalesce(
            Sum('holidays__hours', filter=Q(holidays__type='sick_cert')), Value(0)),

        sick_uncertified_taken=Coalesce(
            Sum('holidays__hours', filter=Q(holidays__type='sick_uncert')), Value(0))
        )

    context = {
        'participants': participants,
        'summary_map': summary_map,
        'departments': current_scheme.department_set.all(),
        'selected_department': dept_id,
        'search_query': search_query,
        'project': current_project,
    }

    return render(request, 'ce/holiday_summary.html', context)


def holidays(request):
    return render(request, "ce/holidays.html")



