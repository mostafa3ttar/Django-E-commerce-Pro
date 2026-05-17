from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account
from django import forms

class AccountCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    
    class Meta:
        model = Account
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'phone_number', 'country')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class AccountAdmin(UserAdmin):
    add_form = AccountCreationForm
    
    list_display = ('email', 'username', 'first_name', 'last_name', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'username')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = () 

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'username', 'phone_number', 'country')}),
        ('Permissions', {'fields': ('is_admin', 'is_staff', 'is_active', 'is_superadmin')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password', 'phone_number', 'country', 'is_active', 'is_staff', 'is_admin', 'is_superadmin'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(form.cleaned_data['password'])
        elif form.cleaned_data.get('password'):
            if not form.cleaned_data['password'].startswith('pbkdf2_'):
                obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

admin.site.register(Account, AccountAdmin)


# @admin.register(Account)
# class AccountAdmin(admin.ModelAdmin):
#     list_display = ['first_name', 'email', 'username']
#     search_fields = ['username']