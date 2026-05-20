from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('',views.home, name='home'),
    path('list_product',views.list_product, name='list_product'),
]
