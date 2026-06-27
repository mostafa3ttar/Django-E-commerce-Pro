# orders/services.py
from django.db import transaction
from django.core.cache import cache
from store.models import Product



def process_order_stock(cart):
    with transaction.atomic():
        for item in cart:
            product = Product.objects.select_for_update().get(id=item['product'].id)
            
            product.stock -= item['quantity']
            product.save()
            cache.delete(f'product_{product.slug}')