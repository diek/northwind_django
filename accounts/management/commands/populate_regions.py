import csv
import os

from django.core.management.base import BaseCommand, CommandError

from accounts.models import Region


class Command(BaseCommand):
    help = "Populate the Region model from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path", type=str, help="Path to the CSV file containing Region data"
        )

    def handle(self, *args, **kwargs):
        csv_path = kwargs["csv_path"]

        if not os.path.exists(csv_path):
            raise CommandError(f"File not found: {csv_path}")

        try:
            with open(csv_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    region_description = row.get("region_description") or row.get(
                        "Region Description"
                    )
                    if region_description:
                        # Create or update region
                        region, created = Region.objects.get_or_create(
                            region_description=region_description.strip()
                        )
                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Created region: {region_description}"
                                )
                            )
                        else:
                            self.stdout.write(
                                f"Region already exists: {region_description}"
                            )
                    else:
                        self.stdout.write(
                            self.style.WARNING("Missing 'region_description' in row")
                        )
        except Exception as e:
            raise CommandError(f"Error processing CSV: {e}")

        self.stdout.write(self.style.SUCCESS("Finished populating regions."))
