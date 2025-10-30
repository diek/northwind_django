import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from user_accounts.models import Employee, EmployeeTerritory, Territory


class Command(BaseCommand):
    help = "Populate EmployeeTerritory from CSV file with employee_id and territory_id"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file_path",
            type=str,
            help="Path to the CSV file containing employee and territory IDs",
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        csv_file_path = kwargs["csv_file_path"]
        with open(csv_file_path, mode="r", newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                employee_id = row["employee_id"]
                territory_id = row["territory_id"]

                # Fetch Employee
                try:
                    employee = Employee.objects.get(pk=employee_id)
                except Employee.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Employee with id {employee_id} does not exist. Skipping."
                        )
                    )
                    continue

                # Fetch Territory
                try:
                    territory = Territory.objects.get(pk=territory_id)
                except Territory.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Territory with id {territory_id} does not exist. Skipping."
                        )
                    )
                    continue

                # Create EmployeeTerritory
                obj, created = EmployeeTerritory.objects.get_or_create(
                    employee=employee, territory=territory
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Added EmployeeTerritory: Employee {employee_id} - Territory {territory_id}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"EmployeeTerritory already exists: Employee {employee_id} - Territory {territory_id}"
                        )
                    )

        self.stdout.write(self.style.SUCCESS("Population completed successfully."))
