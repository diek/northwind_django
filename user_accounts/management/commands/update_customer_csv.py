import csv
import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Update CSV file by adding user_id column starting from 105"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file_path", type=str, help="Path to the CSV file to update"
        )
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help="Path to save the updated CSV file (defaults to overwrite the input file)",
        )

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs["csv_file_path"]
        output_path = kwargs["output"] or csv_file_path

        # Read the CSV file
        with open(csv_file_path, mode="r", newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
            fieldnames = reader.fieldnames

        # Check if 'user_id' already exists
        if "user_id" not in fieldnames:
            fieldnames.append("user_id")

        # Add user_id to each row
        user_id_start = 105
        for idx, row in enumerate(rows):
            row["user_id"] = user_id_start + idx

        # Write back to CSV
        with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        self.stdout.write(
            self.style.SUCCESS(f"CSV file has been updated and saved to {output_path}")
        )
