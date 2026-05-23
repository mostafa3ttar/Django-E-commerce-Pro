from .models import Category 

def categories_to_all_pages(request):
    return {
        'categories': Category.objects.all()
    }
    
