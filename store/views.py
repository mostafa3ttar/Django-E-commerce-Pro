from django.shortcuts import render
from .models import Product


def home(request):
    return render(request, 'store/home.html')

def list_product(request):
    products = Product.objects.filter(status=Product.Status.AVAILABLE)
    context = {'products':products}
    return render(request, 'store/list_product.html', context)