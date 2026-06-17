from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from store.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from django.http import JsonResponse
from coupons.forms import CouponApplyForm



@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, status=Product.Status.AVAILABLE)
    
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'], override_quantity=cd['override'])
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            total_items = len(cart) 
            
            return JsonResponse({
                'status': 'success',
                'total_items': total_items,
                'product_name': product.name
            })
        
        return redirect('cart:cart_detail')
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        
    return redirect('cart:cart_detail')
    
    
    
    
@require_POST
def cart_remove(request, product_id) -> int:
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, status=Product.Status.AVAILABLE)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    
    cart_items = list(cart)
    
    for item in cart_items:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })
        
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'copoun_apply_form': CouponApplyForm(),
    }
    return render(request, 'cart/cart_detail.html', context)