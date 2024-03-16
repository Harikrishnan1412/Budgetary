from django.shortcuts import redirect, render
from django.views import View
import json
from django.http import JsonResponse
from django.views.decorators.cache import cache_control
# To call table
from django.contrib.auth.models import User
# Call userperference
from userpreference.models import UserPreference
from validate_email import validate_email
from django.contrib import messages,auth
from django.core.mail import send_mail
from budgetary.settings import EMAIL_HOST_USER
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading

class EmailThread(threading.Thread):
    def __init__(self, subject, message, EMAIL_HOST_USER, recipient_list):
        self.subject = subject
        self.message = message
        self.EMAIL_HOST_USER = EMAIL_HOST_USER
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        send_mail(self.subject, self.message, EMAIL_HOST_USER, self.recipient_list) 


def send1_email(request):
    subject = "New Order is Placed" 
    message = "Dear Customer" + " " + 'Harikrishnan' + " Your account is created"
    email = 'harikrishnan14122000@gmail.com'
    recipient_list = [email]
    send_mail(subject, message, EMAIL_HOST_USER, recipient_list, fail_silently=True) 
    return redirect('expenses')

# Create your views here.
class EmailValidationView(View):
    def post(self,request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({
                'email_error':'email is invalid'
            },status=400)
        if(User.objects.filter(email=email).exists()):
            return JsonResponse({
                'email_error':' sorry email in use, choose differnet one'
            },status=409)
        return JsonResponse({'email_valid': True})



class UsernameValidationView(View):
    def post(self,request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({
                'username_error':'username should only contain alpha numerical'
            },status=400)
        if(User.objects.filter(username=username).exists()):
            return JsonResponse({
                'username_error':' sorry username in use, choose differnet one'
            },status=409)
        return JsonResponse({'username_valid': True})


class RegistrationView(View):
    def get(self,request):
        return render(request,'authentication/register.html')

    def post(self,request):

        #messages.success(request, 'Success Whatsapp')
        #sample for other messages
        # messages.warning(request, 'Success Whatsapp')
        # messages.info(request, 'Success Whatsapp')
        # messages.error(request, 'Success Whatsapp')

        context = {
            'Fieldvalue':request.POST
        }

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password)<6:
                    messages.error(request,"Password too short")
                    return render(request,'authentication/register.html', context)
                user = User.objects.create_user(username=username,email=email)
                user.set_password(password)
                user.is_active = False
                user.save()
                UserPreference.objects.create(user=user,currency='INR - Indian Rupee')
                # Creating token for authentication and Email activation
                # Creating uidb64 from user uith user primary key
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                # Create token from utils and token_generator by passing user value
                # Getting domain
                domain  = get_current_site(request).domain
                # Get variables from url
                link = reverse('activate', kwargs={'uidb64':uidb64, 'token':token_generator.make_token(user)})
                activate_url = 'http://'+domain+link

                # Send Email
                subject = 'Activate your account' 
                message = 'Hi '+user.username+','+' \nplease use this like to verify your account\n'+activate_url
                email = user.email
                recipient_list = [email]
                # send_mail(subject, message, EMAIL_HOST_USER, recipient_list, fail_silently=True) 
                EmailThread(subject, message, EMAIL_HOST_USER, recipient_list).start()
                # End of email send

                messages.success(request,"Check your for Account Activation mail")
                return render(request,'authentication/register.html')

                
        return render(request,'authentication/register.html')
    

class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('login')

        except Exception as ex:
            pass

        return redirect('login')

# Login in class

class LoginView(View):
    def get(self,request):
        return render(request,'authentication/login.html')
    def post(self,request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                messages.success(request, 'Welcome '+user.username+ ' you are now loggedin')
                auth.login(request, user)
                print("Redirect after logedIn")
                print(user.is_active)
                print(user)
                print(request.user.is_authenticated)
                return redirect('expenses')
            messages.error(request, 'Invalid credencials, try again')
            return render(request,'authentication/login.html')
        messages.error(request, 'Please fill all fields')
        return render(request,'authentication/login.html')
    

#Logout view
class LogoutView(View):
    def post(self,request):
        print("inside Logout")
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')

class RequestPasswordReset(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')
    
    def post(self, request):
        email = request.POST['email']
        context = {
            'values':request.POST
        }
        if not validate_email(email):
            messages.error(request, 'Please supply Valid Email')
            return render(request, 'authentication/reset-password.html', context)
        
        # Send Email
        domain  = get_current_site(request).domain
        # Get User
        user = User.objects.filter(email=email)
        # Get variables from url
        uidb64 = urlsafe_base64_encode(force_bytes(user[0].pk))
        link = reverse('reset-user-password', kwargs={'uidb64':uidb64, 'token':PasswordResetTokenGenerator().make_token(user[0])})
        reset_url = 'http://'+domain+link
        subject = 'Activate your account' 
        message = 'Hi there, \nPlease click this link below to reset the password\n'+reset_url
        email = email
        recipient_list = [email]
        EmailThread(subject, message, EMAIL_HOST_USER, recipient_list).start()
        # send_mail(subject, message, EMAIL_HOST_USER, recipient_list, fail_silently=True) 
        # End of email send

        messages.success(request,"Check Your Mail for Password reset Link")
        return render(request, 'authentication/reset-password.html')
    

class CompletePasswordReset(View):
    def get(self, request,uidb64, token):
        context = {
            'uidb64':uidb64,
            'token':token
        }

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'Password link is invalid, Please request new one')
                return render(request, 'authentication/set-newpassword.html', context)
        except Exception as identifier:
            pass
        return render(request, 'authentication/set-newpassword.html', context)
    
    def post(self, request,uidb64, token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        password = request.POST['password']
        password2= request.POST['password2']
        if password != password2:
            messages.error(request, 'Password do not match')
            return render(request, 'authentication/set-newpassword.html', context)
        if(len(password)<6):
            messages.error(request, 'Password too short')
            return render(request, 'authentication/set-newpassword.html', context)
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfully, you can login with new password')
            return redirect('login')
        except Exception as identifier:
            messages.info(request, 'Somthing went wrong,try again') 
            return render(request, 'authentication/set-newpassword.html', context)
