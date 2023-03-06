from django.contrib.auth.models import User
from validate_email import validate_email 
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib import auth
from django.views import View
from django.core.mail import EmailMessage
import json
import os

# Email verification url
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator

# Create your views here.
class UsernameValidationView(View):
    def post(self, request):
        data=json.loads(request.body)
        username=data['username']
        # check if contain alphanumeric characters
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username should only contain alphanumeric characters'}, status=400)
        # check if exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Sorry username in use,choose another one'}, status=409)
         
        return JsonResponse({'username_valid': True})


class EmailValidationView(View):
    def post(self, request):
        data=json.loads(request.body)
        email=data['email']
        # check if contain alphanumeric characters
        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)
        # check if exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Sorry email in use,choose another one'}, status=409)
         
        return JsonResponse({'email_valid': True})

class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')
  
    def post(self, request):
        # messages.success(request,'Success yes success')
        # messages.warning(request,'Success warning')
        # messages.info(request,'Success info')
        # messages.error(request,'Success err')
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']

        # retain data in the view 
        context = {
            'fieldValues': request.POST
        }
        
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                 
                 if len(password)<6:
                    messages.error(request, 'Password too short')
                    return render(request, 'authentication/register.html',context)
                
        user= User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.is_active = False
        
        
        # send email
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        link = reverse('activate',kwargs={'uidb64':uidb64,'token':token_generator.make_token(user)})
        activate_url = 'http://'+domain+link
        subject = ('Activate Your account buana')
        message = 'Hi '+user.username+ 'Please use this link to verify your account\n' + activate_url
        email = EmailMessage(subject, message, to=[email] )
        if email.send():
            messages.success(request, 'Account successfully created') 
        else:
            messages.success(request, 'Problem sendin email')   
        # send_mail(subject, message, 'info@multiapp.co.ke', ['koometest@gmail.com'])
        # email = 'koometest@gmail.com'
        # send_mail(
        #     subject,
        #     message,
        #     'info@multiapp.co.ke', # from Email
        #     ['koometest@gmail.com',], # To email  
        # )    
        user.save()
        return render(request, 'authentication/register.html')

# for verification 
class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user,token):
                return redirect('login'+'?message='+'User already activated')

            # check if user is_active or not
            if user.is_active:
                return redirect('login')
            user.is_active=True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('login')

        except Exception as ex:
            pass

        return redirect('login')

# render login page
class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, '+user.username+' You are now logged in')
                    return redirect('expenses')

                messages.error(request, 'Account is not active, please check your email')
                return render(request, 'authentication/login.html')

            messages.error(request, 'Username or Password is incorrect!')
            return render(request, 'authentication/login.html')
        
        messages.error(request, 'Please fill all fields!')
        return render(request, 'authentication/login.html')


# render logout page
class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have successfully logged out')
        return redirect('login')

        