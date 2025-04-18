from django.db import models
from django.core.exceptions import ValidationError
import re
from datetime import date
from django.core.validators import RegexValidator


""" -----------------------------------  VALIDATORS  -------------------------------------------------------------- """

# Validate the phone number
numeric_validator = RegexValidator(regex=r'^\d+$', message='Enter a valid phone number (digits only).')


# Validate the PPN Number
def validate_ppsn(ppsn):
    pattern = r'^\d{7}[A-Z]{1,2}$'
    if not re.match(pattern, ppsn):
        raise ValidationError('PPS Number is not valid, please check and re-enter.')


def validate_iban(iban):
    # Remove all whitespace characters (spaces, tabs, etc.)
    cleaned = re.sub(r"\s+", "", iban.upper())

    # Irish IBAN regex (strictly for Ireland)
    pattern = r"^IE\d{2}[A-Z]{4}\d{14}$"

    if re.match(pattern, cleaned):
        return True, cleaned
    else:
        raise ValidationError('IBAN is not valid, please check and re-enter.')


""" -------------------------------------  MODELS  --------------------------------------------------------------- """


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Participant(models.Model):

    # ------------------------- DATABASE FIELDS -------------------- #
    ppsn = models.CharField(
        max_length=9,
        unique=True,
        validators=[validate_ppsn],
        verbose_name='PPS Number'
    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    birth_date = models.DateField()

    address = models.CharField(max_length=200)

    phone = models.CharField(
        max_length=20,
        validators=[numeric_validator],
        verbose_name='Phone Number',
        blank=True
    )

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email'
    )

    emerg_phone = models.CharField(
        max_length=20,
        validators=[numeric_validator],
        verbose_name='Phone Number',
        blank=True
    )

    manual_expire = models.DateField()

    bank_iban = models.CharField(
        max_length=22,
        unique=True,
        validators=[validate_iban],
        verbose_name='Bank IBAN'
    )

    # --------------------------- METHODS --------------------------- #

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    # Get dynamic age from birthday and current date
    @property
    def age(self):
        today = date.today()
        return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)  # noinspection PyUnresolvedReferences
        )

    # Clean the IBAN before saving
    def clean(self):
        super().clean()
        valid, cleaned = validate_iban(self.bank_iban)
        self.bank_iban = cleaned


