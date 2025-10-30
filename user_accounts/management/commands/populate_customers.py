import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from user_accounts.models import CustomerContact, NorthWindUser


class Command(BaseCommand):
    help = "Import CustomerContact data from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file_path",
            type=str,
            help="Path to the CSV file containing customer contact data",
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        csv_file_path = kwargs["csv_file_path"]
        with open(csv_file_path, mode="r", newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                customer_id = row["customer_id"]
                user_id = row["user_id"]
                # Retrieve the associated user
                try:
                    user = NorthWindUser.objects.get(pk=user_id)
                except NorthWindUser.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"User with id {user_id} does not exist. Skipping customer_id {customer_id}."
                        )
                    )
                    continue

                # Create or update CustomerContact
                contact, created = CustomerContact.objects.update_or_create(
                    customer_id=customer_id,
                    defaults={
                        "user": user,
                        "company_name": row["company_name"],
                        "contact_title": row["contact_title"],
                        "address": row["address"],
                        "city": row["city"],
                        "region": row["region"],
                        "postal_code": row["postal_code"],
                        "country": row["country"],
                        "phone": row["phone"],
                    },
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created CustomerContact with customer_id {customer_id}."
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated CustomerContact with customer_id {customer_id}."
                        )
                    )

        self.stdout.write(self.style.SUCCESS("Import completed successfully."))
