from django.shortcuts import render, get_object_or_404, redirect
from .models import OrderItem, Order, OrderPay
from .forms import OrderCreatedForm, OrderPayForm
from cart.cart import Cart
from .tasks import send_emails_order_create




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
            send_emails_order_create.delay(order_id)
            success = True
            return redirect('orders:pay_order', order_id=order.id)
            
        return render(request, 'orders/checkout.html', {'order':order, 'success':success})
    else:
        form = OrderCreatedForm()
    return render(request, 'orders/checkout.html', {'form':form, 'cart':cart})



def order_pay_by_vodafone(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_pay, created = OrderPay.objects.get_or_create(order=order)
    if request.method == 'POST':
        form = OrderPayForm(request.POST, request.FILES, instance=order_pay)     #instance=order_pay   to update data on database not create a new
        if form.is_valid():
            # order_pay = form.save(commit=False)   #to stop it from save in database
            form.save()
            order.status = 'under_review'
            order.save()
            return redirect('orders:payment_success', order_id=order.id)
    else:
        form = OrderPayForm(instance=order_pay)
    
    context = {
        'order':order,
        'form':form
    }
    
    return render(request, 'orders/pay_form.html', context)


def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/payment_success.html',{'order':order})
