from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from apps.shop.models.order import Order, OrderItem


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    autocomplete_fields = ["product"]


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ["id", "user", "status", "created_at", "updated_at"]
    list_per_page = 50
    search_fields = ["user__telegram_id"]
    list_filter = ["status"]
    autocomplete_fields = ["user"]
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ["id", "order", "product", "quantity", "price", "created_at"]
    list_per_page = 50
    search_fields = ["order__user__telegram_id"]
    autocomplete_fields = ["order", "product"]
