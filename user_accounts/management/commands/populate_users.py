import csv
from datetime import datetime

import djclick as click
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils.timezone import make_aware
from djclick import command

User = get_user_model()


@command()
@click.argument("csv_file", type=click.Path(exists=True))
def command(csv_file):
    """
    Import users from a CSV file into NorthwindUser.

    Example:
        python manage.py import_users populate_users.csv
    """

    with open(csv_file, newline="", encoding="latin1") as f:
        reader = csv.DictReader(f)
        users = []
        created_count = 0
        skipped_count = 0

        with transaction.atomic():
            for row in reader:
                email = row.get("email")
                if not email:
                    skipped_count += 1
                    continue

                # Avoid duplicate imports
                if User.objects.filter(email=email).exists():
                    skipped_count += 1
                    continue

                user = User(
                    email=email,
                    first_name=row.get("first_name", ""),
                    last_name=row.get("last_name", ""),
                    timezone=row.get("timezone", "UTC"),
                    custom_id=row.get("custom_id", ""),
                    user_type=row.get("user_type", ""),
                    is_active=row.get("is_active", "True").lower() == "true",
                    is_staff=row.get("is_staff", "False").lower() == "true",
                    is_superuser=row.get("is_superuser", "False").lower() == "true",
                    date_joined=parse_date(row.get("date_joined")),
                    last_login=parse_date(row.get("last_login")),
                    password=make_password(row.get("password", None)),
                )

                users.append(user)
                created_count += 1

            User.objects.bulk_create(users)

        click.echo(f"✅ Imported {created_count} users, skipped {skipped_count}.")


def parse_date(value):
    """Convert string to timezone-aware datetime."""
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        # fallback for common CSV date formats
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    return make_aware(dt)
