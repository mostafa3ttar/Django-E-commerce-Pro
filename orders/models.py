from django.db import models, transaction
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
    CITY_CHOICES = [
        ('CAI', 'القاهرة (Cairo)'),
        ('GIZ', 'الجيزة (Giza)'),
        ('ALX', 'الإسكندرية (Alexandria)'),
        ('QAL', 'القليوبية (Qalyubia)'),
        ('GHR', 'الغربية (Gharbia)'),
        ('MNF', 'المنوفية (Monufia)'),
        ('DKH', 'الدقهلية (Dakahlia)'),
        ('SHR', 'الشرقية (Sharqia)'),
        ('BHG', 'البحيرة (Beheira)'),
        ('KSH', 'كفر الشيخ (Kafr El-Sheikh)'),
        ('DMT', 'دمياط (Damietta)'),
        ('PSD', 'بور سعيد (Port Said)'),
        ('ISM', 'الإسماعيلية (Ismailia)'),
        ('SUZ', 'السويس (Suez)'),
        ('FMT', 'الفيوم (Faiyum)'),
        ('BNS', 'بني سويف (Beni Suef)'),
        ('MIN', 'المنيا (Minya)'),
        ('ASY', 'أسيوط (Asyut)'),
        ('SOH', 'سوهاج (Sohag)'),
        ('QNA', 'قنا (Qena)'),
        ('LXR', 'الأقصر (Luxor)'),
        ('ASW', 'أسوان (Aswan)'),
        ('RSE', 'البحر الأحمر (Red Sea)'),
        ('WAD', 'الوادي الجديد (New Valley)'),
        ('MAT', 'مطروح (Matrouh)'),
        ('SIN', 'شمال سيناء (North Sinai)'),
        ('SIS', 'جنوب سيناء (South Sinai)'),
    ]
    city = models.CharField(max_length=3, choices=CITY_CHOICES, default='CAI', verbose_name="المدينة")
    shipping_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="مصاريف الشحن")
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
    coupon = models.ForeignKey(
        'coupons.Coupon', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )
    discount = models.IntegerField(default=0)
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
    
    def get_shipping_rate(self):
        rates = {
            'CAI': 50.00,
            'GIZ': 50.00,
            'QAL': 55.00,
            
            'ALX': 60.00,
            'GHR': 65.00, 'MNF': 65.00, 'DKH': 65.00, 'SHR': 65.00, 
            'BHG': 65.00, 'KSH': 65.00, 'DMT': 65.00,
            
            'PSD': 65.00, 'ISM': 65.00, 'SUZ': 65.00,
            
            'FMT': 70.00, 'BNS': 70.00, 'MIN': 75.00,
            
            'ASY': 80.00, 'SOH': 85.00, 'QNA': 90.00, 'LXR': 95.00, 'ASW': 100.00,
            
            'RSE': 100.00, 'WAD': 120.00, 'MAT': 100.00, 'SIN': 120.00, 'SIS': 120.00,
        }
        return rates.get(self.city, 50.00)
    
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
                
        if not self.shipping_cost:
            self.shipping_cost = self.get_shipping_rate()
            
        super().save(*args, **kwargs)

        OrderPay.objects.get_or_create(order=self)
        
    def get_total_cost(self):
        products_total = sum(item.get_cost() for item in self.items.all())
        return products_total + self.shipping_cost



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
        old_record = OrderPay.objects.filter(pk=self.pk).first()
        is_first_time_paid = self.paid and (not old_record or not old_record.paid)
        super().save(*args, **kwargs)
    
        if self.order:
            new_status = 'paid' if self.paid else 'under_review'
        
            Order.objects.filter(pk=self.order.pk).update(
                paid=self.paid,
                status=new_status
            )
        
            if is_first_time_paid:
                from orders.services import process_order_stock
                from .tasks import payment_completed
                cart_items = [
                    {'product': item.product, 'quantity': item.quantity} 
                    for item in self.order.items.all()
                ]
            
                transaction.on_commit(lambda: process_order_stock(cart_items))
                transaction.on_commit(lambda: payment_completed.delay(self.order.id))



