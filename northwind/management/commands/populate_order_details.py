import csv
from collections import Counter
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from northwind.models import Order, OrderDetail, Product


class Command(BaseCommand):
    help = "Import order details from a pipe-delimited CSV file."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to the CSV file containing order detail data (pipe-delimited).",
        )

    def handle(self, *args, **options):
        csv_file = options["csv_file"]

        self.stdout.write(self.style.NOTICE(f"📄 Reading file: {csv_file}"))

        try:
            with open(csv_file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="|")

                created_count = 0
                skipped_count = 0
                error_types = Counter()

                with transaction.atomic():
                    for i, row in enumerate(reader, start=2):
                        try:
                            order = self.get_order(row.get("order_id"))
                            product = self.get_product(row.get("product_id"))

                            unit_price = self.safe_decimal(row.get("unit_price"))
                            quantity = self.safe_int(row.get("quantity"))
                            discount = self.safe_decimal(
                                row.get("discount"), allow_null=True
                            )

                            # Validate fields
                            if unit_price is None or unit_price < 0:
                                raise ValueError(f"Invalid unit_price: {unit_price}")
                            if quantity is None or quantity < 1:
                                raise ValueError(f"Invalid quantity: {quantity}")
                            if discount is None:
                                discount = 0
                            if not (0 <= discount <= 1):
                                raise ValueError(f"Invalid discount: {discount}")

                            OrderDetail.objects.create(
                                order=order,
                                product=product,
                                unit_price=unit_price,
                                quantity=quantity,
                                discount=discount,
                            )
                            created_count += 1

                        except Exception as e:
                            skipped_count += 1
                            error_types[type(e).__name__] += 1
                            self.stderr.write(
                                self.style.WARNING(
                                    f"⚠️ Line {i}: Failed to import order detail "
                                    f"(order_id={row.get('order_id', '?')}, product_id={row.get('product_id', '?')}) — {e}"
                                )
                            )

                # Summary
                self.stdout.write(self.style.SUCCESS("✅ Import completed"))
                self.stdout.write(self.style.SUCCESS(f"Created: {created_count}"))
                self.stdout.write(self.style.WARNING(f"Skipped: {skipped_count}"))
                if skipped_count > 0:
                    self.stdout.write("Error breakdown:")
                    for err, count in error_types.items():
                        self.stdout.write(f"  • {err}: {count}")

        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_file}")
        except Exception as e:
            raise CommandError(f"Unexpected error: {e}")

    # --- Helper methods ---

    def get_order(self, order_id):
        if not order_id or str(order_id).strip().upper() in {"NULL", "NONE", ""}:
            raise ValueError("Missing order_id")
        try:
            return Order.objects.get(pk=int(order_id))
        except (Order.DoesNotExist, ValueError):
            raise ValueError(f"Order not found (id={order_id})")

    def get_product(self, product_id):
        if not product_id or str(product_id).strip().upper() in {"NULL", "NONE", ""}:
            raise ValueError("Missing product_id")
        try:
            return Product.objects.get(pk=int(product_id))
        except (Product.DoesNotExist, ValueError):
            raise ValueError(f"Product not found (id={product_id})")

    def safe_int(self, value):
        if not value or str(value).strip().upper() in {"NULL", "NONE", ""}:
            return None
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Invalid integer: '{value}'")

    def safe_decimal(self, value, allow_null=False):
        if not value or str(value).strip().upper() in {"NULL", "NONE", ""}:
            if allow_null:
                return None
            return Decimal("0")
        try:
            return Decimal(value)
        except Exception:
            raise ValueError(f"Invalid decimal value: '{value}'")
