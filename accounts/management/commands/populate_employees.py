import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import (
    Employee,
    NorthWindUser,
)


class Command(BaseCommand):
    help = "Populate Employee model from a pipe-delimited CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file", type=str, help="Path to the pipe-delimited CSV file"
        )
        parser.add_argument(
            "--skip-errors",
            action="store_true",
            help="Continue processing even if individual records fail",
        )

    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        skip_errors = options["skip_errors"]

        try:
            with open(csv_file, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file, delimiter="|")

                # Verify headers
                expected_headers = {
                    "employee_id",
                    "title",
                    "title_of_courtesy",
                    "dob",
                    "hire_date",
                    "address",
                    "city",
                    "region",
                    "postal_code",
                    "country",
                    "home_phone",
                    "extension",
                    "notes",
                    "reports_to",
                }

                if set(reader.fieldnames) != expected_headers:
                    raise CommandError(
                        f"CSV headers don't match expected headers.\n"
                        f"Expected: {expected_headers}\n"
                        f"Found: {set(reader.fieldnames)}"
                    )

                employees_data = []
                reports_to_map = {}  # Store reports_to relationships for later

                for row in reader:
                    employees_data.append(row)

                self.stdout.write(f"Found {len(employees_data)} employees to process")

                # Process in a transaction
                with transaction.atomic():
                    created_count = 0
                    updated_count = 0
                    error_count = 0

                    # First pass: Create/update employees without reports_to
                    self.stdout.write("First pass: Creating/updating employees...")
                    for row in employees_data:
                        try:
                            employee = self._process_employee(row)
                            if employee:
                                if hasattr(employee, "_created"):
                                    created_count += 1
                                else:
                                    updated_count += 1

                                # Store reports_to for second pass (only if not empty or null)
                                reports_to_value = row["reports_to"].strip().upper()
                                if reports_to_value and reports_to_value not in (
                                    "NULL",
                                    "NONE",
                                    "",
                                ):
                                    reports_to_map[row["employee_id"].strip()] = row[
                                        "reports_to"
                                    ].strip()
                        except Exception as e:
                            error_count += 1
                            if skip_errors:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"Error processing employee {row['employee_id']}: {str(e)}"
                                    )
                                )
                            else:
                                raise CommandError(
                                    f"Error processing employee {row['employee_id']}: {str(e)}"
                                )

                    # Second pass: Set reports_to relationships
                    self.stdout.write(
                        f"\nSecond pass: Setting reports_to relationships for {len(reports_to_map)} employees..."
                    )
                    for employee_id, reports_to_id in reports_to_map.items():
                        try:
                            self._set_reports_to(employee_id, reports_to_id)
                        except Exception as e:
                            error_count += 1
                            if skip_errors:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"Error setting reports_to for employee {employee_id}: {str(e)}"
                                    )
                                )
                            else:
                                raise CommandError(
                                    f"Error setting reports_to for employee {employee_id}: {str(e)}"
                                )

                # Output results
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nSuccessfully processed employees:\n"
                        f"  Created: {created_count}\n"
                        f"  Updated: {updated_count}\n"
                        f"  Errors: {error_count}"
                    )
                )

        except FileNotFoundError:
            raise CommandError(f"File '{csv_file}' not found")
        except Exception as e:
            raise CommandError(f"An error occurred: {str(e)}")

    def _process_employee(self, row):
        """Process a single employee record (without reports_to)"""
        employee_id = row["employee_id"].strip()

        # Get or create the NorthWindUser
        try:
            user = NorthWindUser.objects.get(custom_id=employee_id)
        except NorthWindUser.DoesNotExist:
            raise Exception(f"NorthWindUser with custom_id={employee_id} not found")

        # Prepare employee data
        employee_data = {
            "title": row["title"].strip(),
            "title_of_courtesy": row["title_of_courtesy"].strip(),
            "dob": self._parse_date(row["dob"]),
            "hire_date": self._parse_date(row["hire_date"]),
            "address": row["address"].strip(),
            "city": row["city"].strip(),
            "region": row["region"].strip(),
            "postal_code": row["postal_code"].strip(),
            "country": row["country"].strip(),
            "home_phone": row["home_phone"].strip(),
            "extension": row["extension"].strip(),
            "notes": row["notes"].strip(),
        }

        # Create or update employee
        employee, created = Employee.objects.update_or_create(
            user=user, defaults=employee_data
        )

        if created:
            employee._created = True

        return employee

    def _set_reports_to(self, employee_id, reports_to_id):
        """Set the reports_to relationship for an employee"""
        try:
            # Get employee by their user's custom_id
            user = NorthWindUser.objects.get(custom_id=employee_id)
            employee = Employee.objects.get(user=user)

            # Get the manager by their user's custom_id
            manager_user = NorthWindUser.objects.get(custom_id=reports_to_id)
            manager_employee = Employee.objects.get(user=manager_user)

            employee.reports_to = manager_employee
            employee.save(update_fields=["reports_to"])

            self.stdout.write(
                f"  Set employee {employee_id} to report to {reports_to_id}"
            )
        except NorthWindUser.DoesNotExist as e:
            raise Exception(
                f"User not found - employee_id: {employee_id}, reports_to_id: {reports_to_id}"
            )
        except Employee.DoesNotExist as e:
            raise Exception(
                f"Employee not found - employee_id: {employee_id}, reports_to_id: {reports_to_id}"
            )

    def _parse_date(self, date_str):
        """Parse date string, return None if empty"""
        date_str = date_str.strip()
        if not date_str:
            return None

        # Try common date formats
        from datetime import datetime

        formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        raise ValueError(f"Unable to parse date: {date_str}")
