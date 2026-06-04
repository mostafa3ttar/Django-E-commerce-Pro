from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery
from cart.forms import CartAddProductForm
from django.http import JsonResponse
from django.template.loader import render_to_string


def home(request):
    return render(request, 'store/home.html')

def list_product(request, category_slug=None):
    category = None
    selected_slug = category_slug or request.GET.get('category')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if selected_slug == 'best_seller':
            products = Product.objects.filter(status=Product.Status.AVAILABLE, is_best_seller=True)
            
        elif selected_slug and selected_slug != 'all':
            category = get_object_or_404(Category, slug=selected_slug)
            products = Product.objects.filter(status=Product.Status.AVAILABLE, category=category)
            
        else:
            products = Product.objects.filter(status=Product.Status.AVAILABLE)
            
    else:
        if selected_slug == 'best_seller':
            products = Product.objects.filter(status=Product.Status.AVAILABLE, is_best_seller=True)
            
        elif selected_slug:
            category = get_object_or_404(Category, slug=selected_slug)
            products = Product.objects.filter(status=Product.Status.AVAILABLE, category=category)
            
        else:
            products = Product.objects.filter(status=Product.Status.AVAILABLE)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('store/product_cards.html', {'products': products}, request=request)
        return JsonResponse({'html': html})
    context = {'products':products,
            'category':category,
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

