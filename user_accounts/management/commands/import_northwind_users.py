import csv
import secrets
import string
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import make_aware
from django.db import transaction
from user_accounts.models import NorthWindUser


class Command(BaseCommand):
    help = "Import users from a CSV file into the NorthWindUser model"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    def generate_password(self, length=12):
        chars = string.ascii_letters + string.digits + string.punctuation
        return "".join(secrets.choice(chars) for _ in range(length))

    @transaction.atomic
    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        created_count = 0
        updated_count = 0

        try:
            with open(csv_file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="|")
                for row in reader:
                    email = row.get("email")
                    if not email:
                        self.stdout.write(
                            self.style.WARNING("Skipping row with no email")
                        )
                        continue

                    password = row.get("password")
                    if not password:
                        password = self.generate_password()

                    user, created = NorthWindUser.objects.update_or_create(
                        email=email,
                        defaults={
                            "first_name": row.get("first_name", "").strip(),
                            "last_name": row.get("last_name", "").strip(),
                            "is_staff": row.get("is_staff", "False").strip().lower()
                            == "true",
                            "is_active": row.get("is_active", "True").strip().lower()
                            == "true",
                            "is_superuser": row.get("is_superuser", "False")
                            .strip()
                            .lower()
                            == "true",
                            "timezone": row.get("timezone", "UTC").strip(),
                            "custom_id": row.get("custom_id", "").strip(),
                            "user_type": row.get(
                                "user_type", NorthWindUser.UserType.CUSTOMER
                            ).strip(),
                        },
                    )

                    # Set password properly (hashed)
                    user.set_password(password)

                    # Handle date_joined
                    date_joined_str = row.get("date_joined")
                    if date_joined_str:
                        try:
                            parsed_date = make_aware(
                                datetime.fromisoformat(date_joined_str)
                            )
                            user.date_joined = parsed_date
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Invalid date_joined for {email}: {e}"
                                )
                            )

                    user.save()

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Import completed: {created_count} created, {updated_count} updated."
                )
            )

        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_file}")
        except Exception as e:
            raise CommandError(f"Error importing users: {e}")
