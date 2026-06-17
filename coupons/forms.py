from django import forms





class CouponApplyForm(forms.Form):
    code = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter coupon code', 
            'class': 'form-control', 
            'autocomplete': 'off' 
        })
    )
    
    