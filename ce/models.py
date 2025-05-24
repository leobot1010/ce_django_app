from django.db import models
from django.core.exceptions import ValidationError
import re
from datetime import date
from django.core.validators import RegexValidator
from .utils import generate_app_code, calculate_project_end
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum


""" -----------------------------------  VALIDATORS -------------------------------------------------------------- """

# Validate the Phone Number
numeric_validator = RegexValidator(regex=r'^\d+$', message='Enter a valid phone number (digits only).')


# Validate the PPN Number
def validate_ppsn(ppsn):
    pattern = r'^\d{7}[A-Z]{1,2}$'
    if not re.match(pattern, ppsn):
        raise ValidationError('PPS Number is not valid, please check and re-enter.')


# Validate the Bank IBAN
def validate_iban(iban):
    # Remove all whitespace characters (spaces, tabs, etc.)
    cleaned = re.sub(r"\s+", "", iban.upper())

    # Irish IBAN regex (strictly for Ireland)
    pattern = r"^IE\d{2}[A-Z]{4}\d{14}$"

    if re.match(pattern, cleaned):
        return True, cleaned
    else:
        raise ValidationError('IBAN is not valid, please check and re-enter.')


"""----------------------------------------------------------------------------------------------------------------- """
""" ---------------------------------------  MODELS  --------------------------------------------------------------- """


""" ------------------------------------- SCHEME MODEL ------------------------------------------------------------- """


class Scheme(models.Model):
    name = models.CharField(max_length=100)                                 # CE Scheme name
    county = models.CharField(max_length=50)                                # County
    address = models.TextField()                                            # Address
    gov_code = models.CharField(max_length=50, unique=True)                 # Official dsp code
    app_code = models.CharField(max_length=10, unique=True, blank=True)     # County abbreviated code

    current_project = models.ForeignKey(
        'Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='active_schemes'
    )
    use_departments = models.BooleanField(default=True)                     # Toggle on/off departments
    created_on = models.DateField(auto_now_add=True)                        # CE Scheme sign-up data

    def __str__(self):
        if self.current_project:
            return f"{self.name} (Project {self.current_project.number})"
        return f"{self.name} (No project)"

    def save(self, *args, **kwargs):
        # Auto Generate App Code i.e. County abbrev and number
        if not self.app_code:
            self.app_code = generate_app_code(self.county)

        super().save(*args, **kwargs)


""" ------------------------------------- PROJECT MODEL ------------------------------------------------------------"""


class Project(models.Model):
    scheme = models.ForeignKey('Scheme', on_delete=models.CASCADE, related_name='projects')
    number = models.PositiveIntegerField(help_text="eg. 20, 21, 21")
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        unique_together = ('scheme', 'number')
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.scheme.name} - Project {self.number} ({self.start_date} -> {self.end_date})"

    def save(self, *args, **kwargs):
        # Only auto-calculate end date if it's not already set
        if self.start_date and not self.end_date:
            self.end_date = calculate_project_end(self.start_date)

        super().save(*args, **kwargs)


""" ------------------------------------- DEPARTMENT MODEL ------------------------------------------------------- """


class Department(models.Model):
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('scheme', 'name')

    def __str__(self):
        return self.name


""" ------------------------------------ PARTICIPANT MODEL -------------------------------------------------------- """


class Participant(models.Model):

    # ------------------------------ DATABASE FIELDS ------------------------------- #

    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE)

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

    scheme_start_date = models.DateField()
    scheme_finish_date = models.DateField(null=True, blank=True)

    manual_start_date = models.DateField()
    manual_finish_date = models.DateField(null=True, blank=True)

    bank_iban = models.CharField(
        max_length=22,
        unique=True,
        validators=[validate_iban],
        verbose_name='Bank IBAN'
    )

    # ---------------------------------- METHODS --------------------------------- #

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def calculate_current_cycle_entitlement(self):
        """Calculate how many full weeks a participant is active during the current scheme cycle."""
        scheme_cycle_start = self.scheme.current_proj_start
        scheme_cycle_end = self.scheme.current_proj_end

        participant_start = max(self.scheme_start_date, scheme_cycle_start)
        participant_end = min(self.scheme_finish_date, scheme_cycle_end)

        if participant_start > participant_end:
            return Decimal('0.00')

        full_days = (participant_end - participant_start).days
        full_weeks = full_days // 7

        return Decimal(full_weeks) * Decimal('1.56')

    @property
    def holiday_hours_taken(self):
        total = self.holidays.aggregate(Sum('hours'))['hours__sum']
        return total or Decimal('0.00')

    @property
    def holiday_hours_remaining(self):
        return self.current_cycle_entitlement - self.holiday_hours_taken


    @property
    def age(self):
        """ Get dynamic age from date of birth and current date """
        today = date.today()
        return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
                )

    # Clean the IBAN before saving
    def clean(self):
        super().clean()
        valid, cleaned = validate_iban(self.bank_iban)
        self.bank_iban = cleaned


""" ------------------------------------ HOLIDAY SUMMARY MODEL ----------------------------------------------------- """
""" Each record holds all the calculated holiday and sick-leave info for one participant in one project year """
""" ---------------------------------------------------------------------------------------------------------------- """


class HolidaySummary(models.Model):

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='holidays_summaries')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='holiday_summaries')

    # ---------------------------- Holidays -----------------------------------------

    hol_hours_entitled = models.DecimalField(max_digits=6, decimal_places=2)
    hol_hours_taken = models.DecimalField(max_digits=6, decimal_places=2)
    hol_hours_in_lieu = models.DecimalField(max_digits=6, decimal_places=2)

    @property
    def hours_remaining(self):
        return (self.hol_hours_entitled + self.hol_hours_in_lieu) - self.hol_hours_taken

    # --------------------------- Sick Cert -----------------------------------------

    sick_cert_hours_entitled = models.DecimalField(max_digits=6, decimal_places=2)
    sick_cert_hours_taken = models.DecimalField(max_digits=6, decimal_places=2)

    @property
    def sick_cert_hours_remaining(self):
        return self.sick_cert_hours_entitled - self.sick_cert_hours_taken

    # --------------------------- Sick Uncert ---------------------------------------

    sick_uncert_hours_entitled = models.DecimalField(max_digits=6, decimal_places=2)
    sick_uncert_hours_taken = models.DecimalField(max_digits=6, decimal_places=2)

    @property
    def sick_uncert_hours_remaining(self):
        return self.sick_uncert_hours_entitled - self.sick_uncert_hours_taken

    # --------------------------- Metadata -----------------------------------------

    calculated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.participant} | Project {self.project.number} | {self.hours_remaining} hrs left"

    def _weeks_active(self):
        start = max(self.participant.scheme_start_date, self.project.start_date)
        end = min(self.participant.scheme_finish_date, self.project.end_date)
        days = max((end - start).days, 0)
        return days // 7


""" ------------------------------------ HOLIDAY EVENT MODEL ------------------------------------------------------- """


class HolidayEvent(models.Model):

    HOLIDAY_TYPE_CHOICES = [
        ('take_hours', 'Take Hours'),
        ('add_hours', 'Add Hours'),
        ('sick_cert', 'Sick Leave (Cert)'),
        ('sick_uncert', 'Sick Leave (No Cert)'),
        ('other', 'Other'),
    ]

    # ----------------- DATABASE FIELDS -------------- #

    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name='holidays'
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='holiday_event',
        help_text = "Project associated with this holiday Event"
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True)

    date = models.DateField()

    hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Use negative for time off, positive for extra work."
    )

    type = models.CharField(
        max_length=20,
        choices=HOLIDAY_TYPE_CHOICES,
        default='take_hours'
    )

    note = models.CharField(max_length=200, blank=True)

    # -------------------------------- METHODS ----------------------------------- #

    class Meta:
        ordering = ['-date']

    def __str__(self):
        sign = "+" if self.hours > 0 else ""
        return f"{self.participant} | {self.date} | {sign}{self.hours} hrs | {self.get_type_display()}"

    def clean(self):
        super().clean()
        if self.hours == Decimal('0.00'):
            raise ValidationError("Hours cannot be zero.")





