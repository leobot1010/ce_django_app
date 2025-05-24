from .constants import COUNTY_PREFIXES
from datetime import timedelta


def generate_app_code(county):
    """
    Auto generate unique app code for each newly added scheme.
    Format: County abbreviation + 3 character int, starting from 001
    EG: 5th scheme added in Kerry would be KY005
    """
    from .models import Scheme
    prefix = COUNTY_PREFIXES[county]
    count = Scheme.objects.filter(app_code__startswith=prefix).count()
    return f"{prefix}{count + 1:03}"


def calculate_project_end(start_date):
    """
    Given a Monday `start_date`, return the Friday of the week, 52 weeks later.
    """
    if start_date.weekday() != 0:
        raise ValueError("Start date must be a Monday")

    # 52 full weeks = 364 days
    return start_date + timedelta(days=364 - 2)




