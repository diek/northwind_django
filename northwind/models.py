# northwind.models.py
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import Customer, Employee
from config.helpers import TimeStampedModel


class Category(TimeStampedModel):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(_("Category Name"), max_length=255, db_index=True)
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["category_name"]

    def __str__(self):
        return self.category_name or f"Category {self.category_id}"


class Shipper(TimeStampedModel):
    shipper_id = models.AutoField(primary_key=True)
    company_name = models.CharField(_("Company Name"), max_length=255)
    phone = models.CharField(_("Phone"), max_length=50, blank=True)

    class Meta:
        verbose_name = _("Shipper")
        verbose_name_plural = _("Shippers")
        ordering = ["company_name"]

    def __str__(self):
        return self.company_name


class Supplier(TimeStampedModel):
    supplier_id = models.AutoField(primary_key=True)
    company_name = models.CharField(_("Company Name"), max_length=255, db_index=True)
    contact_name = models.CharField(_("Contact Name"), max_length=255, blank=True)
    contact_title = models.CharField(_("Contact Title"), max_length=100, blank=True)
    address = models.CharField(_("Address"), max_length=255, blank=True)
    city = models.CharField(_("City"), max_length=100, blank=True)
    region = models.CharField(_("Region"), max_length=100, blank=True)
    postal_code = models.CharField(_("Postal Code"), max_length=20, blank=True)
    country = models.CharField(_("Country"), max_length=100, blank=True, db_index=True)
    phone = models.CharField(_("Phone"), max_length=50, blank=True)

    class Meta:
        verbose_name = _("Supplier")
        verbose_name_plural = _("Suppliers")
        ordering = ["company_name"]

    def __str__(self):
        return self.company_name


class Product(TimeStampedModel):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(_("Product Name"), max_length=255, db_index=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="products",
        verbose_name=_("Supplier"),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="products",
        verbose_name=_("Category"),
    )
    quantity_per_unit = models.CharField(
        _("Quantity Per Unit"), max_length=100, blank=True
    )
    unit_price = models.DecimalField(
        _("Unit Price"),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    units_in_stock = models.IntegerField(
        _("Units In Stock"), default=0, validators=[MinValueValidator(0)]
    )
    units_on_order = models.IntegerField(
        _("Units On Order"), default=0, validators=[MinValueValidator(0)]
    )
    reorder_level = models.IntegerField(
        _("Reorder Level"), default=0, validators=[MinValueValidator(0)]
    )
    discontinued = models.BooleanField(_("Discontinued"), default=False)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ["product_name"]
        indexes = [
            models.Index(fields=["product_name"]),
            models.Index(fields=["category", "discontinued"]),
        ]

    def __str__(self):
        return self.product_name

    @property
    def is_low_stock(self):
        """Check if product stock is below reorder level."""
        return self.units_in_stock <= self.reorder_level

    @property
    def is_available(self):
        """Check if product is available (not discontinued and in stock)."""
        return not self.discontinued and self.units_in_stock > 0


class Order(TimeStampedModel):
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="orders",
        verbose_name=_("Customer"),
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="orders",
        verbose_name=_("Employee"),
    )
    orderdate = models.DateTimeField(
        _("Order Date"), blank=True, null=True, db_index=True
    )
    required_date = models.DateTimeField(_("Required Date"), blank=True, null=True)
    shipped_date = models.DateTimeField(
        _("Shipped Date"), blank=True, null=True, db_index=True
    )
    ship_via = models.ForeignKey(
        Shipper,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="orders",
        verbose_name=_("Ship Via"),
    )
    freight = models.DecimalField(
        _("Freight"),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    ship_name = models.CharField(_("Ship Name"), max_length=255, blank=True)
    ship_address = models.CharField(_("Ship Address"), max_length=255, blank=True)
    ship_city = models.CharField(_("Ship City"), max_length=100, blank=True)
    ship_region = models.CharField(_("Ship Region"), max_length=100, blank=True)
    ship_postal_code = models.CharField(
        _("Ship Postal Code"), max_length=20, blank=True
    )
    ship_country = models.CharField(_("Ship Country"), max_length=100, blank=True)

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ["-orderdate"]
        indexes = [
            models.Index(fields=["-orderdate"]),
            models.Index(fields=["customer", "-orderdate"]),
            models.Index(fields=["shipped_date"]),
        ]

    def __str__(self):
        return f"Order #{self.order_id} - {self.customer}"

    @property
    def is_shipped(self):
        """Check if order has been shipped."""
        return self.shipped_date is not None

    @property
    def is_overdue(self):
        """Check if order is overdue (required date passed but not shipped)."""
        from django.utils import timezone

        if self.required_date and not self.shipped_date:
            return self.required_date < timezone.now()
        return False


class OrderDetail(TimeStampedModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_details",
        verbose_name=_("Order"),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_details",
        verbose_name=_("Product"),
    )
    unit_price = models.DecimalField(
        _("Unit Price"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    quantity = models.IntegerField(_("Quantity"), validators=[MinValueValidator(1)])
    discount = models.DecimalField(
        _("Discount"),
        max_digits=4,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )

    class Meta:
        db_table = "order_detail"
        verbose_name = _("Order Detail")
        verbose_name_plural = _("Order Details")
        unique_together = ("order", "product")
        indexes = [
            models.Index(fields=["order", "product"]),
        ]

    def __str__(self):
        return f"{self.order} - {self.product} (x{self.quantity})"

    @property
    def subtotal(self):
        """Calculate subtotal before discount."""
        return self.unit_price * self.quantity

    @property
    def total(self):
        """Calculate total after discount."""
        return self.subtotal * (1 - self.discount)

    def save(self, *args, **kwargs):
        """Auto-set unit_price from product if not provided."""
        if not self.unit_price and self.product:
            self.unit_price = self.product.unit_price or 0
        super().save(*args, **kwargs)
