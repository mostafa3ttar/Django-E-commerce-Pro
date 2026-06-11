from django.db import models
from django.utils import timezone
import random
import string
from store.models import Product


def generate_order_id(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))



class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment (في انتظار الدفع)'),
        ('under_review', 'Under Review (قيد المراجعة)'),
        ('paid', 'Paid (تم الدفع والتأكيد)'),
        ('shipped', 'Shipped (تم الشحن)'),
        ('canceled', 'Canceled (ملغي)'),
    ]
    order_id = models.CharField(max_length=8, default=generate_order_id, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=200)
    postal_code = models.PositiveIntegerField()
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    paid = models.BooleanField(default=False)
    
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at'])     #to make filtering more speed 
        ]
        
    def __str__(self):
        return f'Order ID:{self.order_id}'
    
    def get_full_name(self) -> str:
        return self.first_name +' '+ self.last_name
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            unique_id = generate_order_id()
            while Order.objects.filter(order_id=unique_id).exists():
                unique_id = generate_order_id()
            self.order_id = unique_id                                #to save unique_id in DB

        is_new = self.pk is None

        if not is_new:
            try:
                old_order = Order.objects.get(pk=self.pk)
                if old_order.status != 'paid' and self.status == 'paid':
                    self.paid = True
            except Order.DoesNotExist:
                pass
                
        super().save(*args, **kwargs)

        OrderPay.objects.get_or_create(order=self)



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_item', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return str(self.id)
    def get_cost(self):
        return self.price * self.quantity
    
    
class OrderPay(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    pay_phone = models.CharField(max_length=11)
    pay_image = models.ImageField(upload_to='Vodafone_cash/images%y%m%d')
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False, verbose_name="Paid (مدفوع؟)")
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self) -> str:
        return f'Payment for order ID: {self.order.order_id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.order:
            new_status = 'paid' if self.paid else 'under_review'
            
            Order.objects.filter(pk=self.order.pk).update(           #to update Order data(pay) once edit OrderPay data
                paid=self.paid,
                status=new_status
            )
            
            if self.paid:
                from .tasks import send_payment_confirmation_email
                send_payment_confirmation_email.delay(self.order.order_id)     #celery



