from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from store.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from django.http import JsonResponse
from coupons.forms import CouponApplyForm
from django.contrib import messages



@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, status=Product.Status.AVAILABLE)
    form = CartAddProductForm(request.POST, product=product)
    
    if form.is_valid():
        cd = form.cleaned_data
        current_qty = cart.cart.get(str(product_id), {}).get('quantity', 0)
        requested_qty = cd['quantity'] if cd['override'] else current_qty + cd['quantity']
    
        if requested_qty > product.stock:
            error_msg = f"عذراً، المتاح من {product.name} هو {product.stock} فقط."
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect(request.META.get('HTTP_REFERER', 'cart:cart_detail'))
        
        cart.add(product=product, quantity=cd['quantity'], override_quantity=cd['override'])
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'total_items': len(cart), 'product_name': product.name})
        return redirect('cart:cart_detail')
    
    context={
        'product':product,
        'cart_product_form':form
        }
    
    return render(request, 'store/product_detail.html', context)
    
    
    
    
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
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'],
            'override': True},
            product=item['product']
        )
        
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'copoun_apply_form': CouponApplyForm(),
    }
    return render(request, 'cart/cart_detail.html', context)