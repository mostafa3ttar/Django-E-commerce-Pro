from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import Coupon

@receiver(post_save, sender=Coupon)
def clear_product_cache(sender, **kwargs):
    cache.delete('coupon_id')