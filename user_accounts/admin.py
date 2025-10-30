# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    CustomerContact,
    Employee,
    EmployeeTerritory,
    NorthWindUser,
    Region,
    Territory,
)


@admin.register(NorthWindUser)
class NorthWindUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "last_login",
        "is_superuser",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
        "created_at",
        "updated_at",
        "user_type",
        "email",
        "timezone",
    )
    list_filter = (
        "last_login",
        "is_superuser",
        "is_staff",
        "is_active",
        "date_joined",
        "created_at",
        "updated_at",
    )
    raw_id_fields = ("groups", "user_permissions")
    date_hierarchy = "created_at"


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "updated_at",
        "region_id",
        "region_description",
    )
    list_filter = ("created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(Territory)
class TerritoryAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "updated_at",
        "territory_id",
        "territory_description",
        "region",
    )
    list_filter = ("created_at", "updated_at", "region")
    date_hierarchy = "created_at"


@admin.register(CustomerContact)
class CustomerContactAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "updated_at",
        "customer_id",
        "user",
        "company_name",
        "contact_title",
        "address",
        "city",
        "region",
        "postal_code",
        "country",
        "phone",
    )
    list_filter = ("created_at", "updated_at", "user")
    date_hierarchy = "created_at"


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "updated_at",
        "employee_id",
        "user",
        "title",
        "title_of_courtesy",
        "dob",
        "hire_date",
        "address",
        "city",
        "region",
        "postal_code",
        "country",
        "home_phone",
        "extension",
        "notes",
        "reports_to",
    )
    list_filter = (
        "created_at",
        "updated_at",
        "user",
        "dob",
        "hire_date",
        "reports_to",
    )
    raw_id_fields = ("territories",)
    date_hierarchy = "created_at"


@admin.register(EmployeeTerritory)
class EmployeeTerritoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "employee",
        "territory",
        "updated_at",
    )
    list_filter = ("created_at", "employee", "territory", "updated_at")
    date_hierarchy = "created_at"
