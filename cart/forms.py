from django import forms

class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1, 
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'quantity-input',
            'style': 'text-align: center; font-weight: bold;',
            'readonly': True
        })
    )
    
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
    
    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        if self.product:
            self.fields['quantity'].widget.attrs.update({'max': self.product.stock})
            self.fields['quantity'].initial = 1

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if self.product and quantity > self.product.stock:
            raise forms.ValidationError(f"عذراً، المتاح في المخزن هو {self.product.stock} فقط.")
        if quantity <= 0:
            raise forms.ValidationError("يجب أن تكون الكمية أكبر من صفر.")
        return quantity