from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from .models import Order
from django.conf import settings
from .models import Order

from django.template.loader import render_to_string
import weasyprint
from io import BytesIO       # to save libirary in memory not hard disk



@shared_task
def send_emails_order_create(order_id) -> str:
    try:
        order = Order.objects.select_related('coupon').get(order_id=order_id)
        
        sub_total = sum(item.get_cost() for item in order.items.all())
        shipping_cost = order.get_shipping_rate()
        
        discount_amount = 0.0
        if order.coupon:
            discount_amount = float(sub_total) * (order.discount / 100.0)
            
        paid_amount = float(sub_total) - discount_amount
        
    except Order.DoesNotExist:
        return f"Order {order_id} not found."

    subject = f'طلبك رقم [{order.order_id}] قيد المراجعة'

    message = f"Hello {order.get_full_name().title()},\n\n"
    message += f"استلمنا طلبك بنجاح، وفريقنا بدأ في تجهيزه بكل عناية\n"
    message += f"شكراً لاختيارك BONNY\n\n"
    
    message += f"--- تفاصيل الدفع --- \n"
    message += f"قيمة الطلب: {sub_total:,.2f} جنيه\n"
    if order.coupon:
        message += f"خصم الكوبون: -{discount_amount:,.2f} جنيه\n"
    message += f"المطلوب تحويله (كاش او إنستا باى): {paid_amount:,.2f} جنيه\n\n"
    
    message += f"⚠️ لإتمام طلبك، يرجى تحويل مبلغ ({paid_amount:,.2f} جنيه) "
    message += f"عبر كاش أو إنستا باي على الرقم التالي: [01100103523]\n"
    message += f"ثم قم برفع صورة الإيصال عبر رابط الطلب الخاص بك\n\n"
    
    message += f"📌 ملاحظة: مصاريف الشحن ({shipping_cost} جنيه) سيتم دفعها للمندوب نقداً عند الاستلام\n\n"
    
    message += f"ستصلك الفاتورة التفصيلية للطلب شاملة كافة التفاصيل فور تأكيد عملية الدفع\n\n"
    message += f"نسعد بخدمتك دائماً،\n"
    message += f"فريق BONNY"

    mail_sent = send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [order.email])
    return f"Mail sent status: {mail_sent} for Order {order_id}"



@shared_task
def payment_completed(order_id): 
    try:
        order = Order.objects.prefetch_related('items__product').get(id=order_id)
        shipping_cost = order.get_shipping_rate()

        sub_total = sum(item.get_cost() for item in order.items.all())

        discount_amount = 0.0
        if order.coupon:
            discount_amount = float(sub_total) * (order.discount / 100.0)

        paid_amount = float(sub_total) - discount_amount

        total_cost = paid_amount + float(shipping_cost)

        total_before_discount = float(sub_total) + float(shipping_cost)

        city_name_arabic = order.city 

        subject = f'تأكيد استلام الدفع لطلبك رقم #{order.order_id}'
        
        message = f"أهلاً {order.get_full_name().title()},\n\n"
        message += f"شكراً لاختيارك BONNY. نؤكد لك استلامنا لقيمة الطلب بنجاح، وبدأ فريقنا حالياً في تجهيز شحنتك\n\n"
        
        message += f"تجد في المرفقات الفاتورة التفصيلية لطلبك شاملة كافة الحسابات\n\n"
        
        message += f"📌 ملاحظة بخصوص الشحن:\n"
        message += f"مصاريف الشحن ({shipping_cost:,.2f} جنيه) سيتم تحصيلها من قِبل المندوب نقداً عند استلام الشحنة\n\n"
        
        message += f"نسعد بخدمتك دائماً،\n"
        message += f"فريق BONNY"
        
        from_email = settings.DEFAULT_FROM_EMAIL
        email_user = [order.email]
        
        from_email = settings.DEFAULT_FROM_EMAIL
        email_user = [order.email]
        
        context = {
            'order': order,
            'sub_total': f"{sub_total:,.2f}",
            'discount_amount': discount_amount,
            'total_cost': f"{total_cost:,.2f}",
            'city_name_arabic': city_name_arabic,
        }

        if not hasattr(order, 'get_discount_amount'):
            order.get_discount_amount = lambda: discount_amount
        if not hasattr(order, 'get_total_cost_before_discount'):
            order.get_total_cost_before_discount = lambda: total_before_discount

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