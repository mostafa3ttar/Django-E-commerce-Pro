from django.contrib import admin
from .models import Order, OrderItem, OrderPay
import csv
import datetime
from django.http import HttpResponse

from django.utils.safestring import mark_safe
from django.urls import reverse



def order_pdf(obj):
    url = reverse('orders:admin_order_pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}" target="_blank">PDF</a> ')
order_pdf.short_description = 'Invoice'



def export_to_csv(modeladmin, request, queryset):             # modeladmin=order & request=admin request & queryset=data extract to excel
    
    # Http Response
    opts = modeladmin.model._meta                    # model_meta to access Order
    content_disposition = f'attachment; filename={opts.verbose_name}.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition
    
    # Write into CSV file
    writer = csv.writer(response)
    
    required_fields_names = [
        'order_id', 
        'first_name', 
        'last_name', 
        'email', 
        'address', 
        'postal_code', 
        'created_at',
        'status'
    ]
    
    fields = [opts.get_field(field_name) for field_name in required_fields_names]     # to get coloumns
    
    writer.writerow(field.verbose_name for field in fields)     # to get rows
    
    for obj in queryset:
        date_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%a, %d %b %Y at %I:%M %p')
            date_row.append(value)
        writer.writerow(date_row)
    return response
                
export_to_csv.short_description = 'Export to CSV'





class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'email', 'order_id', 'status', 'paid', 'created_at', order_pdf]
    list_filter = ['status', 'paid', 'created_at']
    inlines = [OrderItemInline]
    actions = [export_to_csv]

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