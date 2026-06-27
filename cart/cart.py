from django.conf import settings
from decimal import Decimal
from store.models import Product
from coupons.models import Coupon




class Cart:
    """
    Manage cart items
    """
    
    def __init__(self, request):          # Dunder or Magic method
        self.session = request.session
        
        cart = self.session.get(settings.CART_SESSION_ID)
        
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
            
        self.cart = cart
        self.coupon_id = self.session.get('coupon_id')
        
        self.cleanup_cart()
        
    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity':0, 'price':str(product.price)}
            
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
            
        else:
            self.cart[product_id]['quantity'] += quantity
            
        self.save()
        
    
    def cleanup_cart(self):
        for product_id in list(self.cart.keys()):
            if not Product.objects.filter(id=product_id).exists():
                del self.cart[product_id]
                
    def save(self):
        self.session.modified = True
        
        
    def remove(self, product) -> str:
        product_id = str(product.id)
        
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
            
            
    def __iter__(self):                                      #To loop on all products
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        for product in products:
            cart[str(product.id)]['product'] = product
            
        for db_id in list(self.cart.keys()):
            if str(db_id) not in [str(p.id) for p in products]:
                del self.cart[db_id]
                self.save()
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item                                               #To return one item not all items like return
    
    
    def __len__(self):                                               #To count all items in the cart
        return sum(item['quantity'] for item in self.cart.values())
    
    
    def get_total_price(self):                                      #To get total price of products
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
    
    
    @property                      # to make coupun attr not function
    def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None
    
    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) * self.get_total_price()
        return Decimal(0)
    
    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()
    
    
    def clear(self):
        self.session.pop(settings.CART_SESSION_ID, None)
        self.save()
        
        