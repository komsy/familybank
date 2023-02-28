from django.contrib.auth.models import User
from validate_email import validate_email 
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib import messages
from django.views import View
import json

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
        user.save()
        subject = ('Activate Your account buana')
        message = ('Test')
        email = EmailMessage(
            subject,
            message,
            'info@multiapp.co.ke',
            [email],
        )
        messages.success(request, 'Account successfully created')  
        return render(request, 'authentication/register.html')




