from django.shortcuts import render, redirect
from .forms import RegisterForm
from .models import Account
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages

#Activation Account
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponse
from django.contrib.auth.tokens import default_token_generator



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            country = form.cleaned_data['country']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, country=country, password=password)
            
            user.phone_number = phone_number
            
            user.save()
            
            
            # User Activate
            domain_name = get_current_site(request)   #To get domain
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain':domain_name,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),  #To cipher id
                'token':default_token_generator.make_token(user),
            })
            
            to_email = form.cleaned_data['email']
            send_mail = EmailMessage(mail_subject, message,to=[to_email])
            send_mail.send()
    
            return redirect('login' + f'?command=verification&mail={email}')
    else:
        form = RegisterForm()
        
        form.fields['password'].widget.attrs.update({'autocomplete': 'new-password'})
        form.fields['phone_number'].widget.attrs.update({'autocomplete': 'off'})
        form.fields['email'].widget.attrs.update({'autocomplete': 'off'})
        
    context = {'form':form,}
    
    return render(request,'accounts/register.html',context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = authenticate(email=email, password=password)
        
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                messages.success(request,'Logged in successfully.')
                return redirect('store:home')
            else:
                messages.error(request, 'Your account not active.')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('accounts:login')
        
    return render(request, 'accounts/login.html')
    

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user=None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated successfully.')
        return redirect('accounts:login')
    else:
        messages.error(request, 'The activation link is invalid or has expired.')
        return redirect('accounts:register')
    
    
        