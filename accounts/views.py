from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from .models import Account
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
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
    
    if request.user.is_authenticated:
        return redirect('store:home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(email=email, password=password)
        
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return redirect('store:home')
            else:
                messages.error(request, 'Your account is not active.')
        else:
            messages.error(request, 'Invalid email or password.')
        return render('accounts:login')
        
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    request.session.flush() 
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')
    

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user=None
        
    if user is not None and default_token_generator.check_token(user, token):
        if user.is_active:
            messages.add_message(request, messages.INFO, 'Your account is already active. Please log in.', extra_tags='warning')
            return redirect('accounts:login')
        user.is_active = True
        user.save()
        return render(request, 'accounts/activate_success.html')
    else:
        return render(request, 'accounts/activate_failed.html')
    
    
@login_required(login_url='accounts:login')
def profile(request):
    user = request.user
    # orders = Order.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'user': user,
        # 'orders': orders,
    }
    
    return render(request, 'accounts/profile.html', context)