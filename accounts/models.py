import zoneinfo

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from config.helpers import TimeStampedModel

from .managers import CustomUserManager


def get_timezone_choices():
    """
    Get dynamic timezone choices from available timezones.
    Using a function ensures no new migrations are needed when timezone list changes.
    """
    return [(tz, tz) for tz in sorted(zoneinfo.available_timezones())]


class NorthWindUser(AbstractUser, TimeStampedModel):
    class UserType(models.TextChoices):
        CUSTOMER = "CUS", _("Customer")
        EMPLOYEE = "EMP", _("Employee")
        ADMINISTRATOR = "ADM", _("Administrator")

    username = None
    user_type = models.CharField(
        max_length=3,
        choices=UserType,
        default=UserType.CUSTOMER,
    )
    email = models.EmailField(_("email address"), unique=True)
    timezone = models.CharField(
        _("Timezone"), max_length=50, choices=get_timezone_choices, default="UTC"
    )
    custom_id = models.CharField(max_length=6)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        db_table = "auth_user"  # Optional: if you want to keep the same table name
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
        ]


class Region(TimeStampedModel):
    region_id = models.AutoField(primary_key=True)
    region_description = models.CharField(_("Region Description"), max_length=255)

    class Meta:
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")
        ordering = ["region_description"]

    def __str__(self):
        return self.region_description


class Territory(TimeStampedModel):
    territory_id = models.CharField(primary_key=True, max_length=20)
    territory_description = models.CharField(_("Territory Description"), max_length=255)
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="territories",
        verbose_name=_("Region"),
    )

    class Meta:
        verbose_name = _("Territory")
        verbose_name_plural = _("Territories")
        ordering = ["territory_description"]

    def __str__(self):
        return f"{self.territory_description} ({self.region})"


class Customer(TimeStampedModel):
    customer_id = models.CharField(primary_key=True, max_length=10)
    user = models.OneToOneField(NorthWindUser, on_delete=models.CASCADE)
    company_name = models.CharField(_("Company Name"), max_length=255, db_index=True)
    contact_title = models.CharField(_("Contact Title"), max_length=100, blank=True)
    address = models.CharField(_("Address"), max_length=255, blank=True)
    city = models.CharField(_("City"), max_length=100, blank=True, db_index=True)
    region = models.CharField(_("Region"), max_length=100, blank=True)
    postal_code = models.CharField(_("Postal Code"), max_length=20, blank=True)
    country = models.CharField(_("Country"), max_length=100, blank=True, db_index=True)
    phone = models.CharField(_("Phone"), max_length=50, blank=True)

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
        ordering = ["company_name"]
        indexes = [
            models.Index(fields=["city", "country"]),
        ]

    def __str__(self):
        return self.company_name or self.customer_id


class Employee(TimeStampedModel):
    employee_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(NorthWindUser, on_delete=models.CASCADE)
    title = models.CharField(_("Job Title"), max_length=100, blank=True)
    title_of_courtesy = models.CharField(
        _("Title of Courtesy"), max_length=25, blank=True
    )
    dob = models.DateField(_("Date of Birth"), blank=True, null=True)
    hire_date = models.DateField(_("Hire Date"), blank=True, null=True, db_index=True)
    address = models.CharField(_("Address"), max_length=255, blank=True)
    city = models.CharField(_("City"), max_length=100, blank=True)
    territories = models.ManyToManyField(
        Territory,
        through="EmployeeTerritory",
        related_name="employees",
        verbose_name=_("Territories"),
    )
    region = models.CharField(_("Region"), max_length=100, blank=True)
    postal_code = models.CharField(_("Postal Code"), max_length=20, blank=True)
    country = models.CharField(_("Country"), max_length=100, blank=True)
    home_phone = models.CharField(_("Home Phone"), max_length=50, blank=True)
    extension = models.CharField(_("Extension"), max_length=10, blank=True)
    notes = models.TextField(_("Notes"), blank=True)
    reports_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="subordinates",
        verbose_name=_("Reports To"),
    )

    class Meta:
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")


class EmployeeTerritory(TimeStampedModel):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="employee_territories",
        verbose_name=_("Employee"),
    )
    territory = models.ForeignKey(
        Territory,
        on_delete=models.CASCADE,
        related_name="territory_employees",
        verbose_name=_("Territory"),
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Employee Territory")
        verbose_name_plural = _("Employee Territories")
        unique_together = ("employee", "territory")
        indexes = [
            models.Index(fields=["employee", "territory"]),
        ]

    def __str__(self):
        return f"{self.employee} - {self.territory}"
