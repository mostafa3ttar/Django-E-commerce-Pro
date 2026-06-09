from celery import shared_task
from django.core.mail import send_mail
from .models import Order
from django.conf import settings
from django.utils import timezone
from .models import OrderItem



@shared_task
def send_emails(order_id) -> str:
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return f"Order {order_id} not found."
    
    order_items = OrderItem.objects.filter(order=order)
    
    order = Order.objects.get(order_id=order_id)
    
    local_order_time = timezone.localtime(order.created_at)
    subject = 'Order Confirmation'
    message = f"Your order has been created successfully.\n"
    message += f"On {local_order_time.strftime('%a, %d %b %Y at %I:%M %p')}\n\n"
    message += f"--- Order Confirmation Details ---\n"
    message += f"Customer Name: {order.first_name.title()}\n"
    message += f"Email: {order.email}\n"
    message += f"Address: {order.address}\n"
    message += f"Order ID: {order.order_id}\n"
    message += f"Postal code: {order.postal_code}\n"
    message += f"---------------------------------------\n\n"

    message += f" Here are your order details:\n"

    total_price = 0
    for item in order_items:
        product_name = item.product.name
        item_total = item.price * item.quantity
        total_price += item_total
        message += f"- Product: {product_name} | Price: ${item.price} | Quantity: {item.quantity}\n"

    message += f"\n---------------------------------------\n"
    message += f"Total Price: ${total_price}\n"
    message += f"---------------------------------------"

    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [order.email]
    
    mail_sent = send_mail(subject, message, email_from, recipient_list)
    return f"Mail sent status: {mail_sent} for Order {order_id}"  