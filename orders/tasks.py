from celery import shared_task
from django.core.mail import send_mail
from .models import Order
from django.conf import settings
from django.utils import timezone
from .models import OrderItem



@shared_task
def send_emails_order_create(order_id) -> str:
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return f"Order {order_id} not found."

    order_items = OrderItem.objects.filter(order=order)

    local_order_time = timezone.localtime(order.created_at)
    formatted_time = local_order_time.strftime('%a, %d %b %Y at %I:%M %p')

    subject = f'طلبك رقم [{order.order_id}] قيد المراجعة'

    message = f"Dear {order.get_full_name().title()},\n\n"
    message += f"We have successfully received your order details, and we are truly delighted to be a part of your day.\n"
    message += f"Thank you for choosing BONNY.\n"
    message += f"Order placed on: {formatted_time}\n\n"

    message += f"--- تفاصيل الطلب ---\n"
    message += f"Order ID: {order.order_id}\n"
    message += f"Email: {order.email}\n"
    message += f"Address: {order.address}\n"
    if order.postal_code:
        message += f"Postal code: {order.postal_code}\n"
    message += f"---------------------------------------\n\n"

    message += f" المنتجات التي قمت باختيارها:\n"
    total_price = 0
    for item in order_items:
        product_name = item.product.name
        item_total = item.price * item.quantity
        total_price += item_total
        message += f"- {product_name} | الكمية: {item.quantity} | السعر: ${item.price}\n"
    
    message += f"\n---------------------------------------\n"
    message += f"إجمالي المبلغ: ${total_price}\n"
    message += f"---------------------------------------\n\n"

    message += f"⚠️ الخطوة التالية والمهمة لإتمام طلبك:\n"
    message += f"يرجى تحويل إجمالي المبلغ (${total_price}) إلى حساب فودافون كاش الخاص بنا على الرقم: [01100103523]\n"
    message += f"ثم قم برفع صورة إيصال التحويل ورقم الهاتف المحول منه عبر رابط الأوردر الخاص بك\n\n"
    message += f"بمجرد تأكيد التحويل من قِبل فريقنا، سنبدأ فوراً في تحضير شحنتك الأنيقة لتصلك في أسرع وقت\n\n"
    message += f"Wear it with elegance,\n"
    message += f"The BONNY Team"

    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [order.email]
    
    mail_sent = send_mail(subject, message, email_from, recipient_list)
    return f"Mail sent status: {mail_sent} for Order {order_id}" 



@shared_task
def send_payment_confirmation_email(order_id) -> str:
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return f"Order {order_id} not found."

    subject = f'تم تأكيد الدفع: طلبك رقم [{order.order_id}] في طريقه إليك'

    message = f"Dear {order.get_full_name().title()},\n\n"
    message += f"Thank you! Your payment for order [{order.order_id}] has been successfully confirmed.\n\n"

    message += f"Your package is now being prepared with care and will be delivered to your doorstep within 72 hours.\n\n"
    
    message += f"We will send you the tracking number as soon as it ships.\n\n"
    
    message += f"Wear it with elegance,\n"
    message += f"The BONNY Team"

    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [order.email]
    
    mail_sent = send_mail(subject, message, email_from, recipient_list)
    return f"Payment confirmation mail sent: {mail_sent} for Order {order_id}"