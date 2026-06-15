from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from .models import Order
from django.conf import settings
from django.utils import timezone
from .models import OrderItem, Order

from django.template.loader import render_to_string
import weasyprint
from io import BytesIO       # to save libirary in memory not hard disk



@shared_task
def send_emails_order_create(order_id) -> str:
    try:
        order = Order.objects.get(order_id=order_id)
        city_dict = {str(k).upper(): v for k, v in Order.CITY_CHOICES}
        order_city_code = str(order.city).upper()
        city_name_arabic = city_dict.get(order_city_code, order.city)
        sub_total = sum(item.get_cost() for item in order.items.all())
        shipping_cost = order.get_shipping_rate()
        total_cost = order.get_total_cost()
        
    except Order.DoesNotExist:
        return f"Order {order_id} not found."

    order_items = OrderItem.objects.filter(order=order)

    local_order_time = timezone.localtime(order.created_at)
    formatted_time = local_order_time.strftime('%a, %d %b %Y at %I:%M %p')

    subject = f'طلبك رقم [{order.order_id}] قيد المراجعة'

    message = f"Dear {order.get_full_name().title()},\n\n"
    message += f"Thank you for choosing BONNY. We have successfully received your order, and we are truly delighted to be a part of your journey.\n\n"
    
    message += f"ORDER SUMMARY:\n"
    message += f"Order ID: #{order.order_id}\n"
    message += f"Date: {formatted_time}\n"
    message += f"----------------------------------------\n\n"

    message += f"ITEMS ORDERED:\n"
    for item in order_items:
        product_name = item.product.name
        item_total = item.price * item.quantity
        message += f"- {product_name} (x{item.quantity}) | Unit: {item.price} EGP | Total: {item_total} EGP\n"
        
    message += f"----------------------------------------\n\n"

    message += f"BILLING DETAILS:\n"
    message += f"- Subtotal: {sub_total} EGP (To be transferred via Vodafone Cash or InstaPay)\n"
    message += f"- Shipping to {city_name_arabic}: {shipping_cost} EGP (Cash on Delivery)\n"
    message += f"- Total Invoice Amount: {total_cost} EGP\n\n"
    message += f"----------------------------------------\n\n"

    message += f"⚠️ الخطوة المتبقية لإتمام طلبك:\n"
    message += f"يرجى تحويل قيمة المنتجات فقط وهي ({sub_total} جنيه) إلى حساب فودافون كاش الخاص بنا على الرقم: [01100103523]\n"
    message += f"ثم قم برفع صورة إيصال التحويل ورقم الهاتف الذي قمت بالتحويل منه عبر رابط الأوردر الخاص بك\n\n"
    
    message += f"📌 ملحوظة بخصوص الشحن:\n"
    message += f"مصاريف الشحن بقيمة ({shipping_cost} جنيه) لم يتم حسابها في التحويل، وسيقوم المندوب بتحصيلها منك كاش عند الاستلام\n\n"
    
    message += f"بمجرد تأكيد تحويلك، سيبدأ فريقنا فوراً في تجهيز شحنتك الأنيقة لتصلك في أسرع وقت\n\n"

    message += f"Wear it with elegance,\n"
    message += f"The BONNY Team"

    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [order.email]
    
    mail_sent = send_mail(subject, message, email_from, recipient_list)
    return f"Mail sent status: {mail_sent} for Order {order_id}" 



@shared_task
def payment_completed(oreder_id):
    try:
        order = Order.objects.prefetch_related('items__product').get(id=oreder_id)
        shipping_cost = order.get_shipping_rate()
        
        subject = f'Your BONNY Order Invoice - #{order.order_id}'
        
        message = f"Dear {order.get_full_name().title()},\n\n"
        message += f"Thank you for choosing BONNY. We are delighted to inform you that your payment has been successfully confirmed, and your order is now being curated with the utmost care.\n\n"
        
        message += f"Attached to this email, you will find your official detailed invoice PDF.\n\n"
        
        message += f"📌 ملحوظة هامة بشأن الشحن:\n"
        message += f"يرجى العلم أن المبلغ الذي تم تأكيد دفعه هو قيمة المنتجات فقط. مصاريف الشحن بقيمة ({shipping_cost} جنيه) سيتم تحصيلها من قِبل المندوب نقداً (كاش) عند استلام الشحنة.\n\n"
        
        message += f"Our team is currently preparing your elegant package to ensure it reaches you as soon as possible.\n\n"
        
        message += f"Wear it with elegance,\n"
        message += f"The BONNY Team"
        
        from_email = settings.DEFAULT_FROM_EMAIL
        email_user = [order.email]
        
        context = {
            'order': order,
            'shipping_cost': shipping_cost,
        }
        
        html = render_to_string('orders/pdf.html', context)
        
        out = BytesIO()
        weasyprint.HTML(string=html).write_pdf(out)
        
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=email_user
        )
        email.attach(f'order_{order.order_id}.pdf', out.getvalue(), 'application/pdf')
        email.send()
        
        return True

    except Order.DoesNotExist:
        return False