from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re


# ---------- VALIDATE PHONE NUMBER ----------- #

numeric_validator = RegexValidator(regex=r'^\d+$', message='Enter a valid phone number (digits only).')


# ---------- VALIDATE PPS NUMBER ------------- #

def validate_ppsn(ppsn):
    pattern = r'^\d{7}[A-Z]{1,2}$'
    if not re.match(pattern, ppsn):
        raise ValidationError('PPS Number is not valid, please check and re-enter.')


# ---------- VALIDATE BANK IBAN ------------- #

def validate_iban(iban):
    # Remove all whitespace characters (spaces, tabs, etc.)
    cleaned = re.sub(r"\s+", "", iban.upper())

    # Irish IBAN regex (strictly for Ireland)
    pattern = r"^IE\d{2}[A-Z]{4}\d{14}$"

    if re.match(pattern, cleaned):
        return True, cleaned
    else:
        raise ValidationError('IBAN is not valid, please check and re-enter.')

