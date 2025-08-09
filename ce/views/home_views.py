from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from ce.models import Scheme
from ce.utils.scheme_utils import get_current_scheme


@login_required
def home(request):
    scheme = get_current_scheme(request)
    print("SCHEME:", scheme)  # Add this line
    return render(request, 'ce/home.html', {'scheme': scheme})

