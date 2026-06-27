from django.shortcuts import render, get_object_or_404, redirect
from .models import OrderItem, Order, OrderPay
from .forms import OrderCreatedForm, OrderPayForm
from cart.cart import Cart
from .tasks import send_emails_order_create
from coupons.models import Coupon
from django.contrib.auth.decorators import login_required
from django.db import transaction

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
import weasyprint


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id) 
    shipping_cost = order.get_shipping_rate()
    
    sub_total = sum(item.get_cost() for item in order.items.all())
    
    discount_amount = 0.0
    if order.coupon:
        discount_amount = float(sub_total) * (order.discount / 100.0)
        
    paid_amount = float(sub_total) - discount_amount
    total_cost = paid_amount + float(shipping_cost)
    
    total_before_discount = float(sub_total) + float(shipping_cost)

    city_name_arabic = order.city 

    context = {
        'order': order,
        'sub_total': f"{sub_total:,.2f}",
        'total_cost': f"{total_cost:,.2f}",
        'city_name_arabic': city_name_arabic,
    }

    if not hasattr(order, 'get_discount_amount'):
        order.get_discount_amount = lambda: discount_amount
    if not hasattr(order, 'get_total_cost_before_discount'):
        order.get_total_cost_before_discount = lambda: total_before_discount

    html = render_to_string('orders/pdf.html', context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.order_id}.pdf'

    weasyprint.HTML(string=html).write_pdf(response)
    
    return response





@login_required(login_url='accounts:login')
def checkout(request):
    cart = Cart(request)
    order = None  
    success = False 
    
    if len(cart) == 0 and request.method == 'GET':
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderCreatedForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()

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
    
    discount = float(cart.get_discount()) if hasattr(cart, 'get_discount') else 0.0
    total_after = float(cart.get_total_price()) - discount

    context = {
        'form': form,
        'cart': cart,
        'order': order,
        'success': success,
        'total_price_after_discount': total_after
    }
    return render(request, 'orders/checkout.html', context)


@login_required(login_url='accounts:login')
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

@login_required(login_url='accounts:login')
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # from .tasks import payment_completed
    # payment_completed.delay(order.order_id) 
    return render(request, 'orders/payment_success.html',{'order':order})
