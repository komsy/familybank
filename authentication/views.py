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
import threading
# reset password with django
from django.contrib.auth.tokens import PasswordResetTokenGenerator,default_token_generator

# Email verification url
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

def run(self):
    self.email.send(fail_silently=False)

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
        
        
        # send email using threading
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        link = reverse('activate',kwargs={'uidb64':uidb64,'token':default_token_generator.make_token(user)})
        activate_url = 'http://'+domain+link
        subject = 'Activate Your account buana'
        message = f'Hi {user.username}, Please use this link to verify your account:\n{activate_url}'
        to_email = [email]

        def send_email():
            email_message = EmailMessage(subject, message, to=to_email)
            email_message.send()

        email_thread = threading.Thread(target=send_email)
        email_thread.start()

        messages.success(request, 'Account successfully created, Check your email to activate the account.')
        
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

class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')


    def post(self, request):
        email = request.POST['email']
        # retain data in the view 
        context = {
            'values': request.POST
        }
        if not validate_email(email):
            messages.error(request, 'Please provide a valid email')
            return render(request, 'authentication/reset-password.html', context)
        
        # send email
        user = User.objects.filter(email=email)
        if user.exists():
            uidb64 = urlsafe_base64_encode(force_bytes(user[0].pk))
            domain = get_current_site(request).domain
            link = reverse('reset-user-password',kwargs={'uidb64':uidb64,'token':default_token_generator.make_token(user[0])})
            reset_url = 'http://'+domain+link
            subject = ('Password reset Instructions')
            message = 'Hi '+user[0].username+ ' Please use this link to verify your account\n' + reset_url
            to_email = [email]

            def send_email():
                email_message = EmailMessage(subject, message, to=to_email)
                email_message.send()

            email_thread = threading.Thread(target=send_email)
            email_thread.start()

            messages.success(request, 'We have sent you an email to reset your password') 
        
            return render(request, 'authentication/reset-password.html')
        else:
            messages.error(request, 'User does not exist')
            return render(request, 'authentication/register.html')
        
class CompletePasswordReset(View):
    def get(self, request, uidb64,token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'Password link is invalid, Please request a new one')
                return render(request, 'authentication/reset-password.html', context)

        except Exception as identifier:
            messages.info(request, 'Something went wrong, Try again')

        return render(request, 'authentication/set-new-password.html', context)
    
    def post(self, request, uidb64,token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }
        password = request.POST['password']
        password2 = request.POST['password']
        if password != password2:
            messages.error(request, 'Password does not match')
            return render(request, 'authentication/set-new-password.html', context)
        if len(password) <6:
            messages.error(request, 'Password too short')
            return render(request, 'authentication/set-new-password.html', context)

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.is_active=True
            user.save()

            messages.success(request, 'Password reset successfully, you can now login with the new password')
            return redirect('login')

        except Exception as identifier:
            messages.info(request, 'Something went wrong, Try again')
            return render(request, 'authentication/set-new-password.html', context)
