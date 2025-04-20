from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import AbstractBaseModel
from apps.shop.models.users import BotUsers


class Order(AbstractBaseModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        COMPLETED = "COMPLETED", _("Completed")
        CANCELLED = "CANCELLED", _("Cancelled")

    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.PENDING,
    )
    amount = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    user = models.ForeignKey(BotUsers, on_delete=models.CASCADE)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.id} - {self.status} - {self.amount}"

    class Meta:
        db_table = "order"
        ordering = ["-created_at"]
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    @classmethod
    def pending_orders(cls):
        return cls.objects.filter(status=cls.Status.PENDING).count()


class OrderItem(AbstractBaseModel):
    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=100, decimal_places=2)

    def __str__(self):
        return f"{self.order} - {self.product} - {self.quantity}"

    class Meta:
        db_table = "order_item"
        ordering = ["-created_at"]
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
