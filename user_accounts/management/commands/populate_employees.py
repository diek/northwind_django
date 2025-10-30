import csv
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from user_accounts.models import Employee, NorthWindUser


class Command(BaseCommand):
    help = "Import Employees from a pipe-separated CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to the employee CSV file (pipe-separated)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        csv_file = options["csv_file"]

        try:
            with open(csv_file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="|")
                employees = []

                for row in reader:
                    try:
                        user = NorthWindUser.objects.get(id=row["user_id"])
                    except NorthWindUser.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"⚠️ Skipping employee {row['employee_id']}: User {row['user_id']} not found"
                            )
                        )
                        continue

                    dob = self.parse_date(row.get("dob"))
                    hire_date = self.parse_date(row.get("hire_date"))

                    employee = Employee(
                        employee_id=row["employee_id"],
                        user=user,
                        title=row.get("title", "").strip(),
                        title_of_courtesy=row.get("title_of_courtesy", "").strip(),
                        dob=dob,
                        hire_date=hire_date,
                        address=row.get("address", "").strip(),
                        city=row.get("city", "").strip(),
                        region=row.get("region", "").strip(),
                        postal_code=row.get("postal_code", "").strip(),
                        country=row.get("country", "").strip(),
                        home_phone=row.get("home_phone", "").strip(),
                        extension=row.get("extension", "").strip(),
                        notes=row.get("notes", "").strip(),
                    )

                    employees.append((employee, row.get("reports_to_id")))

                # Bulk create all employees without reports_to first
                Employee.objects.bulk_create([e for e, _ in employees])

                # Set reports_to relationships after employees exist
                for e, reports_to_id in employees:
                    if reports_to_id:
                        try:
                            e.reports_to = Employee.objects.get(
                                employee_id=reports_to_id
                            )
                            e.save(update_fields=["reports_to"])
                        except Employee.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"⚠️ Employee {e.employee_id}: reports_to {reports_to_id} not found"
                                )
                            )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Successfully imported {len(employees)} employees."
                    )
                )

        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_file}")
        except Exception as e:
            raise CommandError(f"Error processing file: {e}")

    @staticmethod
    def parse_date(value):
        if not value:
            return None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                continue
        return None
