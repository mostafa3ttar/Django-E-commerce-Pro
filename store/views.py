from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery
from cart.forms import CartAddProductForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.cache import cache
from django.db.models import Q

def home(request):
    return render(request, 'store/home.html')

def list_product(request, category_slug=None):
    category = None
    selected_slug = category_slug or request.GET.get('category')
    query = request.GET.get('query', '').strip()
    products = Product.objects.filter(status=Product.Status.AVAILABLE)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and query:
        matched_products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()[:5]
        
        suggestions = []
        for p in matched_products:
            suggestions.append({
                'name': p.name,
                'url': f"/product_detail/{p.slug}/" if hasattr(p, 'slug') else "#", 
                'category': p.category.name if p.category else ''
            })
        return JsonResponse({'suggestions': suggestions})

    if selected_slug == 'best_seller':
        products = Product.objects.filter(status=Product.Status.AVAILABLE, is_best_seller=True)
            
    elif selected_slug and selected_slug != 'all':
        category = get_object_or_404(Category, slug=selected_slug)
        products = Product.objects.filter(status=Product.Status.AVAILABLE, category=category)
            
    if query:
        products = products.filter(
            Q(name__icontains=query) |         
            Q(description__icontains=query) |       
            Q(category__name__icontains=query)  
        ).distinct()
        search_vector = SearchVector('name', 'description', 'category')
        search_query = SearchQuery(query)
        products = products.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(search=search_query).order_by('-rank')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('store/product_cards.html', {'products': products}, request=request)
        return JsonResponse({'html': html})     #to filtring by ajax
    
    context = {'products':products,
            'category':category,
            }
    return render(request, 'store/list_product.html', context)

def product_detail(request, product_slug):
    cache_key = f'product_{product_slug}'
    product = cache.get(cache_key)
    if product is None:
        product = get_object_or_404(Product, slug=product_slug, status=Product.Status.AVAILABLE)  #to get from database
        cache.set(cache_key, product, timeout=60 * 30)   #to get from cache 
    cart_product_form = CartAddProductForm()
    context = {'product':product,
            'cart_product_form':cart_product_form
            }
    return render(request, 'store/product_detail.html', context)



