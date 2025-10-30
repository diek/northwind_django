import csv
from collections import Counter
from datetime import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from northwind.models import Order, Shipper
from user_accounts.models import CustomerContact, Employee


class Command(BaseCommand):
    help = "Import orders from a pipe-delimited CSV file."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to the CSV file containing order data (pipe-delimited).",
        )

    def handle(self, *args, **options):
        csv_file = options["csv_file"]

        self.stdout.write(self.style.NOTICE(f"📄 Reading file: {csv_file}"))

        try:
            with open(csv_file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=",")

                created_count = 0
                skipped_count = 0
                error_types = Counter()

                with transaction.atomic():
                    for i, row in enumerate(
                        reader, start=2
                    ):  # line number (header = 1)
                        try:
                            order_id = self.safe_int(row.get("order_id"))
                            if not order_id:
                                raise ValueError("Missing order_id")

                            customer = self.get_customer(row.get("customer_id"))
                            employee = self.get_employee(row.get("employee_id"))
                            shipper = self.get_shipper(row.get("ship_via"))

                            order_date = self.parse_date(row.get("order_date"))
                            required_date = self.parse_date(row.get("required_date"))
                            shipped_date = self.parse_date(row.get("shipped_date"))

                            freight = self.safe_decimal(row.get("freight"))

                            Order.objects.update_or_create(
                                order_id=order_id,
                                defaults={
                                    "customer": customer,
                                    "employee": employee,
                                    "orderdate": order_date,
                                    "required_date": required_date,
                                    "shipped_date": shipped_date,
                                    "ship_via": shipper,
                                    "freight": freight,
                                    "ship_name": row.get("ship_name", ""),
                                    "ship_address": row.get("ship_address", ""),
                                    "ship_city": row.get("ship_city", ""),
                                    "ship_region": row.get("ship_region", ""),
                                    "ship_postal_code": row.get("ship_postal_code", ""),
                                    "ship_country": row.get("ship_country", ""),
                                },
                            )

                            created_count += 1

                        except Exception as e:
                            skipped_count += 1
                            error_type = type(e).__name__
                            error_types[error_type] += 1
                            self.stderr.write(
                                self.style.WARNING(
                                    f"⚠️ Line {i}: Failed to import order (order_id={row.get('order_id', '?')}) — {e}"
                                )
                            )

                # --- Summary ---
                self.stdout.write(self.style.SUCCESS("✅ Import completed"))
                self.stdout.write(
                    self.style.SUCCESS(f"Created/updated: {created_count}")
                )
                self.stdout.write(self.style.WARNING(f"Skipped: {skipped_count}"))
                if skipped_count > 0:
                    self.stdout.write("Error breakdown:")
                    for err, count in error_types.items():
                        self.stdout.write(f"  • {err}: {count}")

        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_file}")
        except Exception as e:
            raise CommandError(f"Unexpected error: {e}")

    # --- Helpers ---

    def parse_date(self, date_str):
        """Convert date string to datetime or None (handles NULL, None, '')."""
        if not date_str or str(date_str).strip().upper() in {"NULL", "NONE", ""}:
            return None
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        raise ValueError(f"Invalid date format: '{date_str}'")

    def safe_int(self, value):
        """Convert to int safely."""
        if not value or str(value).strip().upper() in {"NULL", "NONE", ""}:
            return None
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Invalid integer: '{value}'")

    def safe_decimal(self, value):
        """Convert to Decimal safely."""
        if not value or str(value).strip().upper() in {"NULL", "NONE", ""}:
            return None
        try:
            return Decimal(value)
        except Exception:
            raise ValueError(f"Invalid decimal value: '{value}'")

    def get_customer(self, customer_id):
        if not customer_id or str(customer_id).strip().upper() in {"NULL", "NONE", ""}:
            return None
        try:
            return CustomerContact.objects.get(pk=customer_id)
        except CustomerContact.DoesNotExist:
            raise ValueError(f"CustomerContact not found (id={customer_id})")

    def get_employee(self, employee_id):
        if not employee_id or str(employee_id).strip().upper() in {"NULL", "NONE", ""}:
            return None
        try:
            return Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            raise ValueError(f"Employee not found (id={employee_id})")

    def get_shipper(self, shipper_id):
        if not shipper_id or str(shipper_id).strip().upper() in {"NULL", "NONE", ""}:
            return None
        try:
            return Shipper.objects.get(pk=shipper_id)
        except Shipper.DoesNotExist:
            raise ValueError(f"Shipper not found (id={shipper_id})")
