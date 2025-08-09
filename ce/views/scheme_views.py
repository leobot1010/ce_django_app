from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ce.models import Scheme, Department
from ce.forms import SchemeForm
from ce.utils.scheme_utils import get_current_scheme


@login_required
def scheme_page(request):
    return render(request, "ce/scheme.html")


@login_required
def edit_scheme(request):
    scheme = get_current_scheme(request)

    if request.method == "POST":
        form = SchemeForm(request.POST, instance=scheme if scheme else None)
        if form.is_valid():
            scheme = form.save()

            # ------------------ DEPARTMENTS ----------------- #

            # Handle checkbox logic
            scheme.departments_disabled = form.cleaned_data.get("departments_disabled", False)

            scheme.save()  # Now save the updated scheme

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