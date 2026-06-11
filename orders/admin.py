from django.contrib import admin
from .models import Order, OrderItem, OrderPay

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'email', 'order_id', 'status', 'paid', 'created_at']
    list_filter = ['status', 'paid', 'created_at']
    inlines = [OrderItemInline]

    @admin.display(description='Customer Name')
    def get_full_name(self, obj):
        first = obj.first_name if obj.first_name else ""
        last = obj.last_name if obj.last_name else ""
        return f"{first} {last}".strip() or "N/A"

@admin.register(OrderPay)
class OrderPayAdmin(admin.ModelAdmin):
    list_display = ['get_customer_name', 'pay_phone', 'pay_image', 'paid']
    list_editable = ['paid'] 

    @admin.display(description='Customer Name')
    def get_customer_name(self, obj):
        if obj.order:
            return f"{obj.order.first_name} {obj.order.last_name}"
        return "N/A"