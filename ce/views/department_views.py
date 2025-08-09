from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from ce.models import Department, Scheme
from django.db import IntegrityError
from ce.utils.scheme_utils import get_current_scheme


@login_required
def manage_departments(request):
    scheme = get_current_scheme(request)
    departments = Department.objects.filter(scheme=scheme).order_by("name")

    # Handle deletion
    delete_id = request.GET.get("delete")
    if delete_id:
        Department.objects.filter(id=delete_id, scheme=scheme).delete()
        return redirect("manage_departments")

    # Handle editing (prefill form)
    edit_id = request.GET.get("edit")
    edit_dept = None
    if edit_id:
        edit_dept = get_object_or_404(Department, id=edit_id, scheme=scheme)

    # Handle add or update form submission
    error = None
    if request.method == "POST":
        raw_name = request.POST.get("name").strip()
        name = raw_name.title()
        if "edit_id" in request.POST:
            dept = get_object_or_404(Department, id=request.POST["edit_id"], scheme=scheme)
            dept.name = name
            try:
                dept.save()
            except IntegrityError:
                error = "A department with this name already exists."
        else:
            try:
                Department.objects.create(name=name, scheme=scheme)
            except IntegrityError:
                error = "This department already exists."

        if not error:
            return redirect("manage_departments")

    context = {
        "scheme": scheme,
        "departments": departments,
        "edit_dept": edit_dept,
        "error": error
    }
    return render(request, "ce/manage-departments.html", context)


