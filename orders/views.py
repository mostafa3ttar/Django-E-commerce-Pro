from django.shortcuts import render, get_object_or_404, redirect
from .models import OrderItem, Order, OrderPay
from .forms import OrderCreatedForm, OrderPayForm
from cart.cart import Cart
from .tasks import send_emails_order_create

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
import weasyprint
import os


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)          # order_id which located in url
    sub_total = sum(item.get_cost() for item in order.items.all())
    context = {
        'order': order,
        'total_cost': order.get_total_cost(),
        'sub_total':sub_total,
    }
    html = render_to_string('orders/pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.order_id}.pdf'
    weasyprint.HTML(string=html).write_pdf(response)
    return response
    






def order_create(request):
    cart = Cart(request)
    order = None  
    success = False 
    
    if request.method == 'POST':
        form = OrderCreatedForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order, 
                    product=item['product'], 
                    price=item['price'], 
                    quantity=item['quantity']
                )
            cart.clear()
            
            order_id = order.order_id
            send_emails_order_create.delay(order_id)
            success = True
            return redirect('orders:pay_order', order_id=order.id)
    else:
        form = OrderCreatedForm()

    context = {
        'form': form,
        'cart': cart,
        'order': order,
        'success': success
    }
    return render(request, 'orders/checkout.html', context)



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
    # from .tasks import payment_completed
    # payment_completed.delay(order.order_id) 
    return render(request, 'orders/payment_success.html',{'order':order})
