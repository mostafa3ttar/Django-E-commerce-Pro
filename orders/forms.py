from django import forms
from .models import Order, OrderPay
from django.core.exceptions import ValidationError
import re


class OrderCreatedForm(forms.ModelForm):
    class Meta:
        model = Order 
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']




class OrderPayForm(forms.ModelForm):
    class Meta:
        model = OrderPay
        fields = ['pay_phone', 'pay_image']

    def clean_pay_phone(self):
        pay_phone = self.cleaned_data.get('pay_phone')  #to access value of attr
        if not pay_phone:
            raise ValidationError('This field is required.')
        
        if not pay_phone.isdigit():
            raise ValidationError('The phone number must contain digits only.')
        
        if len(pay_phone) != 11:
            raise ValidationError('The phone number must be exactly 11 digits.')
        
        phone_pattern = r'^01[0125][0-9]{8}$'
        if not re.match(phone_pattern, pay_phone):
            raise ValidationError('Please enter a valid Egyptian phone number (e.g., 01xxxxxxxxx).')
        
        return pay_phone
    
    