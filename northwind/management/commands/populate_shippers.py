import csv

from django.core.management.base import BaseCommand, CommandError

from northwind.models import Shipper


class Command(BaseCommand):
    help = "Import shippers from a pipe-separated CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_filepath", type=str, help="Path to the CSV file to import"
        )

    def handle(self, *args, **kwargs):
        csv_filepath = kwargs["csv_filepath"]
        try:
            with open(csv_filepath, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile, delimiter="|")
                count = 0
                for row in reader:
                    shipper_id = row.get("shipper_id")
                    company_name = row.get("company_name")
                    phone = row.get("phone", "")

                    if not company_name:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Skipping row with missing company_name: {row}"
                            )
                        )
                        continue

                    # Create or update the Shipper
                    shipper, created = Shipper.objects.update_or_create(
                        shipper_id=shipper_id,
                        defaults={
                            "company_name": company_name,
                            "phone": phone,
                        },
                    )
                    count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully imported {count} shippers.")
                )
        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_filepath}")
        except Exception as e:
            raise CommandError(f"An error occurred: {e}")
