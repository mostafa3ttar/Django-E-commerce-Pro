from django.urls import path
from . import views

app_name='orders'

urlpatterns = [
    path('checkout/', views.order_create, name='checkout'),
    path('pay-order/<int:order_id>/', views.order_pay_by_vodafone, name='pay_order'),
    path('payment-success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('admin/pdf/<int:order_id>/', views.admin_order_pdf, name='admin_order_pdf'),
]
