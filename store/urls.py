from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('',views.home, name='home'),
    path('list_product/',views.list_product, name='list_product'),
    path('category/<slug:category_slug>/',views.list_product, name='product_by_category'),
    path('collection/<slug:collection_slug>/',views.list_product, name='product_by_collection'),
    path('product_detail/<slug:product_slug>/',views.product_detail, name='product_detail'),
    # path('search/', views.product_search, name='product_search' )
]
