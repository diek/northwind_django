import csv

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from northwind.models import Category, Product, Supplier


class Command(BaseCommand):
    help = "Import products from a pipe-separated CSV file"

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
                    product_id = row.get("product_id")
                    product_name = row.get("product_name")
                    supplier_id = row.get("supplier_id")
                    category_id = row.get("category_id")
                    quantity_per_unit = row.get("quantity_per_unit", "")
                    unit_price = row.get("unit_price")
                    units_in_stock = row.get("units_in_stock")
                    units_on_order = row.get("units_on_order")
                    reorder_level = row.get("reorder_level")
                    discontinued_str = row.get("discontinued", "False")

                    # Validate required field
                    if not product_name:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Skipping row with missing product_name: {row}"
                            )
                        )
                        continue

                    # Parse decimal
                    try:
                        unit_price_value = float(unit_price) if unit_price else None
                    except ValueError:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Invalid unit_price '{unit_price}' for product '{product_name}', setting to None"
                            )
                        )
                        unit_price_value = None

                    # Parse integers
                    def parse_int(val):
                        try:
                            return int(val)
                        except (TypeError, ValueError):
                            return 0

                    units_in_stock_val = parse_int(units_in_stock)
                    units_on_order_val = parse_int(units_on_order)
                    reorder_level_val = parse_int(reorder_level)

                    # Parse boolean
                    discontinued = discontinued_str.lower() in ["true", "1", "yes"]

                    # Get related Supplier and Category
                    supplier = None
                    if supplier_id:
                        supplier = Supplier.objects.filter(
                            supplier_id=supplier_id
                        ).first()

                    category = None
                    if category_id:
                        category = Category.objects.filter(
                            category_id=category_id
                        ).first()

                    # Update or create product
                    product, created = Product.objects.update_or_create(
                        product_id=product_id,
                        defaults={
                            "product_name": product_name,
                            "supplier": supplier,
                            "category": category,
                            "quantity_per_unit": quantity_per_unit,
                            "unit_price": unit_price_value,
                            "units_in_stock": units_in_stock_val,
                            "units_on_order": units_on_order_val,
                            "reorder_level": reorder_level_val,
                            "discontinued": discontinued,
                        },
                    )
                    count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully imported {count} products.")
                )
        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_filepath}")
        except Exception as e:
            raise CommandError(f"An error occurred: {e}")
