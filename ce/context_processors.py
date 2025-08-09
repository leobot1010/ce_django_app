from .models import Scheme


def current_scheme(request):
    try:
        scheme = Scheme.objects.first()
    except Scheme.DoesNotExist:
        scheme = None
    return {'scheme': scheme}
