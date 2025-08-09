from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ce.models import Scheme, Department, Participant, Project
from datetime import date, timedelta
from ce.utils.project_utils import calculate_project_dates


class Command(BaseCommand):
    help = "Seed test data for CE Scheme"

    def handle(self, *args, **kwargs):
        # ------------------------- Create User --------------------------- #
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            email="admin@cescheme.com",
            defaults={
                "username": "admin@cescheme.com",
                "first_name": "Admin",
                "last_name": "User",
                "is_staff": True,
            }
        )
        user.set_password("password123")  # Optional password
        user.save()
        self.stdout.write(self.style.SUCCESS("✅ User created or retrieved"))

        # ------------------------- Create Scheme ------------------------- #
        scheme, created = Scheme.objects.get_or_create(
            gov_code="DSP123",
            defaults={
                "name": "Test CE Scheme",
                "county": "Kerry",
                "address": "Main St, Killarney",
                "user": user,
            }
        )
        if not created and scheme.user != user:
            scheme.user = user
            scheme.save()
            self.stdout.write(self.style.SUCCESS("✅ Assigned user to existing scheme"))

        if created:
            self.stdout.write(self.style.SUCCESS(f"✅ Created scheme: {scheme}"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Scheme already exists"))

        # ------------------------- Create Project ------------------------ #
        project_number = 20
        start_date = date(2025, 1, 6)
        end_date, next_project_start, next_project_end = calculate_project_dates(start_date)

        project, project_created = Project.objects.get_or_create(
            scheme=scheme,
            number=project_number,
            defaults={"start_date": start_date, "end_date": end_date},
        )

        if not project_created:
            if project.end_date != end_date or project.start_date != start_date:
                project.start_date = start_date
                project.end_date = end_date
                project.save()
                self.stdout.write(self.style.SUCCESS("✅ Project dates updated"))
            else:
                self.stdout.write(self.style.WARNING("⚠️ Project already exists with correct dates"))
        else:
            self.stdout.write(self.style.SUCCESS("✅ Project created"))

        # ---------------- Update Scheme fields ------------------------- #
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

        # ---------------------- Create Departments ---------------------- #
        dept_names = ["Office", "Outdoor"]
        for name in dept_names:
            Department.objects.get_or_create(scheme=scheme, name=name)
        self.stdout.write(self.style.SUCCESS("✅ Departments created"))

        # -------------------- Create Participants ----------------------- #
        participants = [
            {
                "ppsn": "1234567A",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "bank_iban": "IE29AIBK93115212345678"
            },
            {
                "ppsn": "2345678B",
                "first_name": "Mary",
                "last_name": "Smith",
                "email": "mary@example.com",
                "bank_iban": "IE29AIBK93115287654321"
            },
            {
                "ppsn": "3456789C",
                "first_name": "Liam",
                "last_name": "O'Sullivan",
                "email": "liam@example.com",
                "bank_iban": "IE29AIBK93115213579246"
            },
        ]

        for data in participants:
            participant, created = Participant.objects.get_or_create(
                ppsn=data["ppsn"],
                defaults={
                    "scheme": scheme,
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "birth_date": date(1990, 1, 1),
                    "address": "123 Main St, Killarney",
                    "phone": "0831234567",
                    "email": data["email"],
                    "emerg_phone": "0867654321",
                    "department": scheme.department_set.first(),
                    "scheme_start_date": date(2025, 1, 6),
                    "manual_start_date": date(2025, 1, 8),
                    "scheme_finish_date": date(2028, 1, 1),
                    "manual_finish_date": date(2028, 1, 8),
                    "bank_iban": data["bank_iban"],
                }
            )


            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Participant created: {participant}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Participant already exists: {participant}"))
