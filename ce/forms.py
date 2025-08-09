from django import forms
from .models import Participant, Department, Scheme
from datetime import date, timedelta
from .constants import COUNTY_CHOICES


class SchemeForm(forms.ModelForm):

    county = forms.ChoiceField(choices=COUNTY_CHOICES)
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    new_departments = forms.CharField(
        label="Add Your Scheme's Departments",
        required=False,
        widget=forms.Textarea(attrs={'rows': 2})
    )

    departments_disabled = forms.BooleanField(
        label="Disable Departments",
        required=False,
        initial=True
    )

    class Meta:
        model = Scheme

        fields = [
            'name', 'county', 'address', 'gov_code', 'current_project', 'departments_disabled'
        ]

        labels = {
            'name': 'Scheme Name',
            'county': 'County (based on registration)',
            'address': 'Scheme Address',
            'gov_code': 'Official DSP Code',
            'current_proj_no': 'Current Project Number',
            'current_proj_start': 'Start Date of Current Project',
            'departments_disabled': "We don't use departments",
        }

    def clean(self):
        cleaned_data = super().clean()
        departments_disabled = cleaned_data.get("departments_disabled") or False
        new_departments = cleaned_data.get("new_departments")

        if departments_disabled and new_departments:
            raise forms.ValidationError(
                "You cannot enter departments and also select 'We don't use departments'. "
                "Please uncheck the box or leave the department names."
            )

        return cleaned_data


class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = [
            'ppsn', 'first_name', 'last_name', 'department', 'birth_date', 'address',
            'phone', 'email', 'emerg_phone',
            'scheme_start_date','manual_start_date',
            'bank_iban'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['department'].empty_label = "Choose Department..."

        self.fields['manual_start_date'].help_text = "Date participant last completed manual handing course."

    def clean(self):
        cleaned_data = super().clean()
        birth_date = cleaned_data.get('birth_date')
        manual_start = cleaned_data.get('manual_start_date')
        scheme_start = cleaned_data.get('scheme_start_date')

        today = date.today()

        # Validate Birthdate cannot be in the future
        if birth_date and birth_date > today:
            self.add_error('birth_date', 'Birth date cannot be in the future.')

        return cleaned_data


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']


class ParticipantDateForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = [
            'scheme_start_date',
            'manual_start_date',
            'scheme_finish_date',
            'manual_finish_date',
        ]
        widgets = {
            'scheme_start_date': forms.DateInput(attrs={'type': 'date'}),
            'manual_start_date': forms.DateInput(attrs={'type': 'date'}),
            'scheme_finish_date': forms.DateInput(attrs={'type': 'date'}),
            'manual_finish_date': forms.DateInput(attrs={'type': 'date'}),
        }


