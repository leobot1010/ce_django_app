from django.shortcuts import render, redirect, get_object_or_404
from .forms import ParticipantForm
from .models import Department, Scheme, Participant, HolidaySummary, HolidayEvent
from .forms import DepartmentForm, SchemeForm
from django.contrib import messages
from datetime import date, timedelta
from pprint import pprint
from ce.logic.holiday_summary import calculate_holiday_summary
from django.db.models import Sum, Q, F, Value
from django.db.models.functions import Coalesce


def home(request):
    return render(request, "ce/home.html")


def scheme(request):
    return render(request, "ce/scheme.html")


def holiday_summary(request):
    # Get current scheme from log-in session
    scheme_id = request.session.get('scheme_id')
    current_scheme = Scheme.objects.get(id=scheme_id)

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


def edit_scheme(request):
    scheme = Scheme.objects.first()

    if request.method == "POST":
        form = SchemeForm(request.POST, instance=scheme if scheme else None)
        if form.is_valid():
            scheme = form.save()

            # Handle departments entered in form
            new_depts = form.cleaned_data.get('new_departments')
            if new_depts:
                dept_names = [name.strip() for name in new_depts.split(',') if name.strip()]
                for name in dept_names:
                    Department.objects.get_or_create(scheme=scheme, name=name)

            return redirect('scheme')

    else:
        form = SchemeForm(instance=scheme)

    return render(request, "ce/edit-scheme.html", {'form': form})


def view_participants(request):
    return render(request, "ce/view-participants.html")


def add_participants(request):
    scheme = Scheme.objects.first()

    if request.method == "POST":
        form = ParticipantForm(request.POST)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.scheme = scheme

            participant.manual_finish_date = form.cleaned_data['manual_start_date'] + timedelta(days=1095)
            participant.scheme_finish_date = form.cleaned_data['scheme_start_date'] + timedelta(days=1092)

            participant.save()

            # 👉 Create initial holiday summary for new participant
            if scheme.current_project:
                calculate_holiday_summary(participant, scheme.current_project)

            messages.success(request, "✅ Participant added successfully.")
            return redirect('home')

    else:
        form = ParticipantForm(initial={
            'first_name': 'John',
            'last_name': 'Doe',
            'ppsn': '1234567A',
            'email': 'john@example.com',
            'phone': '0831234567',
            'emerg_phone': '0867654321',
            'address': '123 Main St, Killarney',
            'birth_date': '1990-01-01',
            'manual_start_date': '2022-01-01',
            'scheme_start_date': '2022-01-03',  # must be a Monday
            'bank_iban': 'IE29AIBK93115212345678',
        })

    return render(request, "ce/add-participants.html", {'form': form})


def edit_participants(request):
    return render(request, "ce/edit-participants.html")


def holidays(request):
    return render(request, "ce/holidays.html")


def edit_departments(request):
    departments = Department.objects.all()

    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('edit_departments')
    else:
        form = DepartmentForm()

    return render(request, "ce/edit-departments.html", {
        'form': form,
        'departments': departments,
    })


def delete_departments(request, pk):
    department = get_object_or_404(Department, pk=pk)
    department.delete()
    return redirect('edit_departments')
