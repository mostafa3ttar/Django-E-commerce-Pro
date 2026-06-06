from django.shortcuts import render
from .models import OrderItem
from .forms import OrderCreatedForm
from cart.cart import Cart
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone





def order_create(request):
    cart = Cart(request)
    
    success = False
    if request.method == 'POST':
        form = OrderCreatedForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
            cart.clear()
            local_order_time = timezone.localtime(order.created_at)
            subject = 'Order Confirmation'
            message = f"Your order has been created successfully.\n"
            message += f"On {local_order_time.strftime('%a, %d %b %Y at %I:%M %p')}\n\n"
            message += f"--- Order Confirmation Details ---\n"
            message += f"Customer Name: {form.cleaned_data['first_name'].title()}\n"
            message += f"Email: {form.cleaned_data['email']}\n"
            message += f"Address: {order.address}\n"
            message += f"Order ID: {order.order_id}\n"
            message += f"Postal code: {order.postal_code}\n"
            message += f"---------------------------------------\n\n"

            message += f" Here are your order details:\n"

            for item in cart:
                product_name = item['product'].name
                message += f"- Product: {product_name} | Price: ${item['price']} | Quantity: {item['quantity']}\n"

            message += f"\n---------------------------------------\n"
            message += f"Total Price: ${cart.get_total_price()}\n"
            message += f"---------------------------------------"

            email_from = settings.DEFAULT_FROM_EMAIL
            recipient_list = [form.cleaned_data['email']]

            send_mail(subject, message, email_from, recipient_list)

            
            success = True
        return render(request, 'orders/checkout.html', {'order':order, 'success':success})
    else:
        form = OrderCreatedForm()
    return render(request, 'orders/checkout.html', {'form':form, 'cart':cart})

