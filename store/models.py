from django.db import models
from django.utils.text import slugify
import uuid
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    
    slug = models.SlugField(null=True, blank=True, unique=True, allow_unicode=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            original_slug = slugify(self.name, allow_unicode=True)
            queryset = Category.objects.all()
            
            if not original_slug:
                original_slug = "category"
                
            slug = original_slug
            next_num = 1
            
            while queryset.filter(slug=slug).exists():
                slug = f"{original_slug}-{next_num}"
                next_num += 1
                
            self.slug = slug
            
        super(Category, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.name
    
    def get_category_url(self):
        return reverse('store:product_by_category', args=[self.slug])
    
    
class Product(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'AV', 'Available'
        DRAFT = 'DF', 'Draft'
    name = models.CharField(max_length=250)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='products/images%y%m%d')
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.AVAILABLE)
    description = models.TextField(max_length=1500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_best_seller = models.BooleanField(default=False, verbose_name="Best Seller")
    
    slug = models.SlugField(null=True, blank=True, unique=True, max_length=255, allow_unicode=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            original_slug = slugify(self.name, allow_unicode=True)
            
            if not original_slug:
                original_slug = "product"
                
            self.slug = f"{original_slug}-{str(uuid.uuid4())[:4]}"
            
        super(Product, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.name
    
    def get_product_url(self):
        return reverse('store:product_detail', args=[self.slug])
    
    class Meta:
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
        ]