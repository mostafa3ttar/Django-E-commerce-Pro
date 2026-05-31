from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery
from cart.forms import CartAddProductForm


def home(request):
    return render(request, 'store/home.html')

def list_product(request, category_slug=None):
    category = None
    # categories = Category.objects.all()
    products = Product.objects.filter(status=Product.Status.AVAILABLE)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    context = {'products':products,
            'category':category,
            #    'categories':categories
            }
    return render(request, 'store/list_product.html', context)

def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, status=Product.Status.AVAILABLE)
    cart_product_form = CartAddProductForm()
    context = {'product':product,
            'cart_product_form':cart_product_form
            }
    return render(request, 'store/product_detail.html', context)



def product_search(request):
    query=None
    results = []
    if 'query' in request.GET:
        query = request.GET.get('query')
        search_vector = SearchVector('name', 'description')
        search_query = SearchQuery(query)
        results = Product.objects.annotate(search=search_vector, rank=SearchRank(search_vector,search_query)).filter(search=search_query, status=Product.Status.AVAILABLE).order_by('-rank')    #annotate() To make Temporary table in database when search
        
    context = {
        'query':query,
        'results':results
    }
    
    return render(request, 'store/search.html', context)

