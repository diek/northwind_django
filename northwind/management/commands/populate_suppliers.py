import csv

from django.core.management.base import BaseCommand, CommandError

from northwind.models import Supplier


class Command(BaseCommand):
    help = "Import suppliers from a pipe-separated CSV file"

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
                    supplier_id = row.get("supplier_id")
                    company_name = row.get("company_name")
                    contact_name = row.get("contact_name", "")
                    contact_title = row.get("contact_title", "")
                    address = row.get("address", "")
                    city = row.get("city", "")
                    region = row.get("region", "")
                    postal_code = row.get("postal_code", "")
                    country = row.get("country", "")
                    phone = row.get("phone", "")

                    if not company_name:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Skipping row with missing company_name: {row}"
                            )
                        )
                        continue

                    # Create or update the supplier
                    supplier, created = Supplier.objects.update_or_create(
                        supplier_id=supplier_id,
                        defaults={
                            "company_name": company_name,
                            "contact_name": contact_name,
                            "contact_title": contact_title,
                            "address": address,
                            "city": city,
                            "region": region,
                            "postal_code": postal_code,
                            "country": country,
                            "phone": phone,
                        },
                    )
                    count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully imported {count} suppliers.")
                )
        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_filepath}")
        except Exception as e:
            raise CommandError(f"An error occurred: {e}")
