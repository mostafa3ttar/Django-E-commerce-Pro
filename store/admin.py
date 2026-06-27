from django.contrib import admin
from .models import Category, Product, Collection


admin.site.register(Category)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ['slug']
    list_display = ['name', 'category','price','stock','status']
    list_editable = ['status','stock']
    
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    filter_horizontal = ('products',)
    prepopulated_fields = {'slug': ('title',)}
    list_display = ['title', 'slug']
    list_editable = ['slug']