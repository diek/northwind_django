import csv
import os

from django.core.management.base import BaseCommand, CommandError

from user_accounts.models import Region, Territory


class Command(BaseCommand):
    help = "Populate the Territory model from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path", type=str, help="Path to the CSV file containing Territory data"
        )

    def handle(self, *args, **kwargs):
        csv_path = kwargs["csv_path"]

        if not os.path.exists(csv_path):
            raise CommandError(f"File not found: {csv_path}")

        try:
            with open(csv_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    territory_id = row.get("territory_id")
                    territory_description = row.get("territory_description")
                    region_id = row.get("region_id")  # or 'region_id' based on your CSV

                    if not all([territory_id, territory_description, region_id]):
                        self.stdout.write(
                            self.style.WARNING(
                                f"Skipping row due to missing data: {row}"
                            )
                        )
                        continue

                    # Find the Region instance by description
                    try:
                        region = Region.objects.get(region_id=region_id.strip())
                    except Region.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Region not found for description '{region_desc}', skipping territory '{territory_id}'"
                            )
                        )
                        continue

                    # Create or update the Territory
                    territory, created = Territory.objects.update_or_create(
                        territory_id=territory_id.strip(),
                        defaults={
                            "territory_description": territory_description.strip(),
                            "region_id": region_id,
                        },
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f"Created territory: {territory_id}")
                        )
                    else:
                        self.stdout.write(f"Updated territory: {territory_id}")
        except Exception as e:
            raise CommandError(f"Error processing CSV: {e}")

        self.stdout.write(self.style.SUCCESS("Finished populating territories."))
