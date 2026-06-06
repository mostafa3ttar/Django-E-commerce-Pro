from .models import Category 

def categories_to_all_pages(request):
    return {
        'categories': Category.objects.all()
    }
    
def search_query_context(request):
    return {
        'query': request.GET.get('query', '').strip()
    }