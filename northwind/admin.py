# northwind/admin.py

# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Category, Order, OrderDetail, Product, Shipper, Supplier


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "category_id",
        "category_name",
        "description",
    )
    list_filter = (
        "category_name",
        "description",
    )
    date_hierarchy = "updated_at"


@admin.register(Shipper)
class ShipperAdmin(admin.ModelAdmin):
    list_display = (
        "shipper_id",
        "company_name",
        "phone",
    )
    list_filter = ("company_name", "updated_at")
    date_hierarchy = "updated_at"


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        "supplier_id",
        "company_name",
        "contact_name",
        "contact_title",
        "address",
        "city",
        "region",
        "postal_code",
        "country",
        "phone",
    )
    list_filter = (
        "company_name",
        "contact_name",
    )
    date_hierarchy = "updated_at"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "updated_at",
        "product_id",
        "product_name",
        "supplier",
        "category",
        "quantity_per_unit",
        "unit_price",
        "units_in_stock",
        "units_on_order",
        "reorder_level",
        "discontinued",
    )
    list_filter = (
        "product_name",
        "units_in_stock",
        "supplier",
        "category",
        "discontinued",
    )
    date_hierarchy = "created_at"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "updated_at",
        "order_id",
        "customer",
        "employee",
        "orderdate",
        "required_date",
        "shipped_date",
        "ship_via",
        "freight",
        "ship_name",
        "ship_address",
        "ship_city",
        "ship_region",
        "ship_postal_code",
        "ship_country",
    )
    list_filter = (
        "created_at",
        "updated_at",
        "customer",
        "employee",
        "orderdate",
        "required_date",
        "shipped_date",
        "ship_via",
    )
    date_hierarchy = "orderdate"


@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "unit_price",
        "quantity",
        "discount",
    )
    list_filter = ("order", "product")
