from django.core.management.base import BaseCommand
from ce.models import Scheme, Department, Participant, Project
from datetime import date, timedelta
from ce.utils import calculate_project_end


class Command(BaseCommand):
    help = "Seed test data for CE Scheme"

    def handle(self, *args, **kwargs):

        # -------------------- Create Scheme ------------------------------
        scheme, created = Scheme.objects.get_or_create(
            gov_code="DSP123",
            defaults={
                "name": "Test CE Scheme",
                "county": "Kerry",
                "address": "Main St, Killarney",
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"✅ Created scheme: {scheme}"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Scheme already exists"))

        # ------------------ Create Project ------------------------------
        project_number = 20
        start_date = date(2025, 1, 6)

        # Auto calculate the end-date from start-date
        end_date = calculate_project_end(start_date)

        project, project_created = Project.objects.get_or_create(
            scheme=scheme,
            number=project_number,
            defaults={"start_date": start_date, "end_date": end_date},
        )

        if not project_created:
            print("START:", project.start_date, "END:", project.end_date)
            print("EXPECTED:", start_date, end_date)
            if project.end_date != end_date or project.start_date != start_date:
                project.start_date = start_date
                project.end_date = end_date
                project.save()
                self.stdout.write(self.style.SUCCESS("✅ Project dates updated"))
            else:
                self.stdout.write(self.style.WARNING("⚠️ Project already exists with correct dates"))

        # ------------------ Update Scheme fields -------------------------
        updated = False

        if scheme.current_project != project:
            scheme.current_project = project
            updated = True

        if scheme.app_code != "KY005":
            scheme.app_code = "KY005"
            updated = True

        if updated:
            scheme.save()
            self.stdout.write(self.style.SUCCESS("✅ Scheme updated with current project and app code"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Scheme already has correct project and app code"))

        # ---------------- Create Departments -------------------------------
        dept_names = ["Office", "Outdoor"]
        for name in dept_names:
            Department.objects.get_or_create(scheme=scheme, name=name)
        self.stdout.write(self.style.SUCCESS("✅ Departments created"))

        # Create Participant
        participant, created = Participant.objects.get_or_create(
            ppsn="1234567A",
            defaults={
                "scheme": scheme,
                "first_name": "John",
                "last_name": "Doe",
                "birth_date": date(1990, 1, 1),
                "address": "123 Main St, Killarney",
                "phone": "0831234567",
                "email": "john@example.com",
                "emerg_phone": "0867654321",
                "department": scheme.department_set.first(),
                "scheme_start_date": date(2025, 1, 6),
                "manual_start_date": date(2025, 1, 8),
                "scheme_finish_date": date(2028, 1, 1),
                "manual_finish_date": date(2028, 1, 8),
                "bank_iban": "IE29AIBK93115212345678",
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"✅ Participant created: {participant}"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Participant already exists"))
