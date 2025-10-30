import csv
import os

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Compare two order CSV files and output rows from Orders.csv not found in northwind_order_pq.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            "northwind_file",
            type=str,
            help="Path to northwind_order_pq.csv (comma-separated)",
        )
        parser.add_argument(
            "orders_file", type=str, help="Path to Orders.csv (pipe-separated)"
        )

    def handle(self, *args, **options):
        northwind_path = options["northwind_file"]
        orders_path = options["orders_file"]

        # Ensure files exist
        if not os.path.exists(northwind_path):
            raise CommandError(f"File not found: {northwind_path}")
        if not os.path.exists(orders_path):
            raise CommandError(f"File not found: {orders_path}")

        # Read northwind_order_pq.csv
        self.stdout.write("Reading northwind_order_pq.csv...")
        with open(northwind_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=",")
            northwind_ids = {row["order_id"] for row in reader if row.get("order_id")}

        # Read Orders.csv and find unmatched rows
        self.stdout.write("Comparing Orders.csv...")
        unmatched_rows = []
        with open(orders_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="|")
            fieldnames = reader.fieldnames
            for row in reader:
                order_id = row.get("order_id")
                if order_id and order_id not in northwind_ids:
                    unmatched_rows.append(row)

        # Prepare fixtures folder
        fixtures_dir = os.path.join(os.getcwd(), "fixtures")
        os.makedirs(fixtures_dir, exist_ok=True)

        # Write unmatched rows
        output_file = os.path.join(fixtures_dir, "orders_not_in_northwind.csv")
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(unmatched_rows)

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ {len(unmatched_rows)} unmatched orders written to {output_file}"
            )
        )
