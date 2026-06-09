from django.shortcuts import render
from .models import OrderItem
from .forms import OrderCreatedForm
from cart.cart import Cart
from .tasks import send_emails




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
            
            order_id = order.order_id

            send_emails.delay(order_id)
            
            success = True
        return render(request, 'orders/checkout.html', {'order':order, 'success':success})
    else:
        form = OrderCreatedForm()
    return render(request, 'orders/checkout.html', {'form':form, 'cart':cart})

