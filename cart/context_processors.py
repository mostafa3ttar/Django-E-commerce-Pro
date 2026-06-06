from .cart import Cart


def cart(request):
    return {'cart':Cart(request)}

def cart_context(request):
    cart_data = request.session.get('cart', {})
    total_items = sum(item.get('quantity', 1) for item in cart_data.values())
    
    cart_products = []
    
    return {
        'cart_total_items': total_items,
        'cart_mini_products': cart_products,
    }