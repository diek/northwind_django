import csv

from django.core.management.base import BaseCommand, CommandError

from northwind.models import Category


class Command(BaseCommand):
    help = "Import categories from a CSV file with pipe separator"

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
                    category_id = row.get("category_id")
                    category_name = row.get("category_name")
                    description = row.get("description", "")

                    if not category_name:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Skipping row with missing category_name: {row}"
                            )
                        )
                        continue

                    # Create or update the category
                    category, created = Category.objects.update_or_create(
                        category_id=category_id,
                        defaults={
                            "category_name": category_name,
                            "description": description,
                        },
                    )
                    count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully imported {count} categories.")
                )
        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_filepath}")
        except Exception as e:
            raise CommandError(f"An error occurred: {e}")
