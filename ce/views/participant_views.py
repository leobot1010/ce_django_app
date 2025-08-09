from django.shortcuts import render, redirect
from ce.models import Scheme, Participant
from datetime import date, timedelta
from ce.forms import ParticipantForm, ParticipantDateForm
from django.contrib import messages
from ce.utils.holiday_utils import create_or_update_holiday_summary
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from ce.utils.scheme_utils import get_current_scheme


@login_required
def view_participants(request):
    scheme = get_current_scheme(request)
    participants = Participant.objects.filter(scheme=scheme).order_by('first_name')

    return render(request, 'ce/view-participants.html', {
        'participants': participants,
        'scheme': scheme,
    })


@login_required
def add_participants(request, participant_id=None):
    scheme = get_current_scheme(request)

    participant = None
    is_editing = False

    if participant_id:
        participant = get_object_or_404(Participant, id=participant_id, scheme=scheme)
        is_editing = True

    if request.method == "POST":
        form = ParticipantForm(request.POST, instance=participant)

        if form.is_valid():
            participant = form.save(commit=False)
            participant.scheme = scheme

            participant.manual_finish_date = form.cleaned_data['manual_start_date'] + timedelta(days=1095)
            participant.scheme_finish_date = form.cleaned_data['scheme_start_date'] + timedelta(days=1092)

            participant.save()

            if not is_editing and scheme.current_project:
                create_or_update_holiday_summary(participant, scheme.current_project)

            messages.success(
                request,
                "✅ Participant updated successfully." if is_editing else "✅ Participant added successfully."
            )
            return redirect('view_participants')
    else:
        form = ParticipantForm(instance=participant)

    return render(request, 'ce/participant-form.html', {
        'form': form,
        'form_title': 'Edit Participant' if is_editing else 'Add Participant',
        'submit_label': 'Update' if is_editing else 'Submit'
    })


@login_required
def edit_participant_dates(request, participant_id):
    scheme = get_current_scheme(request)
    participant = get_object_or_404(Participant, id=participant_id, scheme=scheme)

    original_manual_start = participant.manual_start_date
    original_scheme_start = participant.scheme_start_date

    form = ParticipantDateForm(request.POST or None, instance=participant)

    if request.method == 'POST':
        if form.is_valid():
            participant = form.save()

            # Optional: recalculate finish dates automatically
            participant.manual_finish_date = participant.manual_start_date + timedelta(days=1095)
            participant.scheme_finish_date = participant.scheme_start_date + timedelta(days=1092)
            participant.save()

            # Recreate holiday summary if start date changed
            if (participant.manual_start_date != original_manual_start or
                    participant.scheme_start_date != original_scheme_start):
                create_or_update_holiday_summary(participant, scheme.current_project)

            messages.success(request, "✅ Participant dates updated successfully.")
            return redirect('view_participants')

    return render(request, 'ce/edit-participant-dates.html', {
        'form': form,
        'participant': participant,
    })


@login_required
def delete_participants(request):
    participants = Participant.objects.all().order_by('first_name', 'last_name')  # Optional: sort alphabetically
    return render(request, 'ce/delete-participants.html', {
        'participants': participants
    })

