from ce.constants import COUNTY_PREFIXES


def get_current_scheme(request):
    """
    Returns the Scheme instance linked to the currently logged-in user.
    Assumes a OneToOneField from Scheme to User.
    """
    from ce.models import Scheme

    if request.user.is_authenticated:
        return Scheme.objects.filter(user=request.user).first()
    return None


def generate_app_code(county):
    """
    Auto generate unique app code for each newly added scheme.
    Format: County abbreviation + 3 character int, starting from 001
    EG: 5th scheme added in Kerry would be KY005
    """
    from ce.models import Scheme
    prefix = COUNTY_PREFIXES[county]
    count = Scheme.objects.filter(app_code__startswith=prefix).count()
    return f"{prefix}{count + 1:03}"



