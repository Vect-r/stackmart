from django.shortcuts import render, redirect
from django.contrib import messages
from apps.master.utils.inputValidators import *
from apps.master.auth.utils import *
from apps.users.models import User, UserVerification
from django.views.decorators.cache import never_cache
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from datetime import datetime, timedelta, UTC
from apps.users.forms import PasswordResetForm
from .mailings import MailSender
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
from django.utils import timezone

mailObj = MailSender()

# Create your views here.
def index(request):
    if request.isAuthenticated:
        return redirect('dashboard')
    
    return render(request, "dashboard/index.html")

def login(request):
    if request.method == "POST":
        try:
            email = is_valid_email(request.POST.get('email'))
            password = request.POST.get('password')

            getUser = User.objects.get(email=email)
            if not getUser.is_active:
                messages.error(request, "Your account is pending approval. Once Approved we will send you a mail. Please Contact Support for any queries")
                return redirect('login')
        
            if not verify_password(password, getUser.password):
                messages.error(request, "Incorrect Email or Password")
                return redirect('login')

            if getUser:
                getUser.last_login = timezone.now()
                getUser.save()
                token = generate_token(getUser)
                
                response = redirect('dashboard')
                # Securely set the cookie
                # response.set_cookie('access_token', token, httponly=True)
                request.session['access_token'] = token
                return response
        
        except ValidationError as e:
            messages.error(request, e)
            return redirect("login")
        
        except User.DoesNotExist:
            messages.error(request,"User does not exist. Please Try again...")
            return redirect("login")
              
    return render(request, "dashboard/login.html")

@login_required_jwt
def dashboard(request):
    user = request.authenticated_user
    return render(request,'dashboard/dashboard.html',{'user':user})

def about(request):
    return render(request, "dashboard/about.html")



@never_cache
def register(request):
    if request.method=="POST":
        try:
            user_type_ = request.POST['user_type']
            pancard_ = request.FILES['pancard']
            username_ = validateUsername(request.POST['username'])
            email_ = is_valid_email(request.POST['email'])
            if User.objects.filter(email=email_).exists():
                messages.error(request, "Email already exists. Please Login or Reset Password")
                return redirect("register")
            mobile_ = is_valid_mobile(request.POST['mobile'])
            password_ = hash_password(validatePassword(match_password(request.POST['password'],request.POST['confirm_password'])))

            print(user_type_,pancard_,email_,mobile_,password_)
            new_user = User.objects.create(
                username=username_,
                user_type=user_type_,
                email=email_,
                mobile=mobile_,
                pancard=pancard_,
                password=password_
            )
            new_user.save()
            vObj = UserVerification()
            vObj.verification_type = "email"
            vObj.user = new_user
            vObj.expiryDateTime = datetime.now(UTC)+timedelta(days=1)
            vObj.save()
            mailObj.sendMailVerification(new_user,vObj.id,request)
            
            messages.success(request,"Account Created Sucessfully...")
            return redirect('login')
        except ValidationError as e:
            messages.error(request, e)
            return redirect("register")
    return render(request, "dashboard/create_user.html")

def logout(request):
    messages.success(request,"User Logged Out")
    request.session.flush()
    return redirect('index')

def contact(request):
    return render(request, "dashboard/contact.html")

def forgot_password(request):
    if request.method=="POST":
        try:
            email_ = is_valid_email(request.POST['email'])
            getUser = User.objects.get(email=email_)
            if getUser:
                vObj = UserVerification()
                vObj.verification_type = 'password'
                vObj.user = getUser
                vObj.expiryDateTime = datetime.now(UTC)+timedelta(days=1)
                vObj.save()
                print(vObj.id)
                
                # subject = 'Reset Your Stackmart Credentials'
                # domain = get_current_site(request).domain
                # reset_url = f"http://{domain}/reset-password/{vObj.id}/"
                
                # # 1. Render the HTML template with data
                # html_message = render_to_string('dashboard/mails/password_reset.html', {
                #     'user': getUser,
                #     'reset_url': reset_url,
                # })
                
                # # 2. Create a plain text version (for email clients that disable HTML)
                # plain_message = strip_tags(html_message)
                
                # # 3. Send
                # send_mail(
                #     subject,
                #     plain_message,
                #     settings.DEFAULT_FROM_EMAIL,  # e.g., 'system@stackmart.dev'
                #     [email_],
                #     html_message=html_message,
                #     fail_silently=False,
                # )
                mailObj.sendPasswordReset(request,vObj.id,getUser,email_)
                messages.success(request,f'Password Reset mail has been sent to {email_}. Please check your Inbox')
                return redirect('login')
        except ValidationError as e:
            messages.success(request,e)
            return redirect('forget_password')
    return render(request, "dashboard/forgot_password.html")

def reset_password(request,tokenId):
    try:
        getVerificationTicket = UserVerification.objects.get(id=tokenId)
        form = PasswordResetForm() 
        if getVerificationTicket.isTimeExpired or getVerificationTicket.isVerifiedByUser:
            form=None
            validLink=False
        else:
            validLink=True
    except UserVerification.DoesNotExist:
        form = None
        validLink=False
        # return render(request, 'dashboard/reset_password.html', {
        # 'validlink': False,  # <--- Forces the "Valid" UI state
        # 'form': None  

    if request.method=="POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            password_ = form.cleaned_data["password"]
            getUser = getVerificationTicket.user
            getUser.password = hash_password(password_)
            getUser.save()
            getVerificationTicket.isVerifiedByUser = True
            getVerificationTicket.save()
            subject = 'Security Alert: Password Changed'
            html_message = render_to_string('dashboard/mails/password_reset_success.html', {
                'user': getUser,
            })
            plain_message = strip_tags(html_message)

        # 3. Send the notification
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [getUser.email],
                html_message=html_message,
                fail_silently=True, # Don't crash the user flow if mail fails
            )
            messages.success(request,'Password Reset Successful.')
            return redirect('login')
    return render(request, 'dashboard/reset_password.html', {
        'validlink': validLink,  # <--- Forces the "Valid" UI state
        'form': form,
        'token': tokenId
    })

def verifyNewMail(request,tokenId):
    try:
        vObj = UserVerification.objects.get(id=tokenId)
        if vObj.isTimeExpired or vObj.isVerifiedByUser:
            status = False
        else:
            status = True
            vObj.isVerifiedByUser = True
            vObj.save()
    except UserVerification.DoesNotExist:
        status = False

    if vObj.user.is_active:
        approval = ""
    else:
        approval = "But your account is pending approval. Once Approved we will send you a mail. Please Contact Support for any queries."    
    
    return render(request,'dashboard/mail_verification.html',{'valid_link':status,
                                                              'approval':approval})
    
@login_required_jwt
def profile(request):
    user = request.authenticated_user
    isDefaultAvatar=User._meta.get_field('profile').get_default()==user.profile
    return render(request,'dashboard/profile.html',{'user':user,'isDefaultAvatar':isDefaultAvatar})

@login_required_jwt
@require_POST
def profileUpdate(request):
    user = request.authenticated_user
    
    # 1. Handle Text Data
    email = request.POST.get('email')
    mobile = request.POST.get('mobile')
    remove_avatar = request.POST.get('remove_avatar') # Check for removal flag
    
    # Validation
    message = ""
    try:
        if email and email != user.email:
            if type(user).objects.filter(email=email).exclude(pk=user.pk).exists():
                return JsonResponse({'status': 'error', 'message': 'Email already in use.'}, status=400)
            user.email = is_valid_email(email)
            message += f"Verification Mail has been sent to {email}. Please verify it within 24 Hours or your account will be deactivated."
            vObj = UserVerification(verification_type="email",user = user,expiryDateTime = timezone.now()+timedelta(days=1))
            vObj.save()
            mailObj.sendMailVerification(user,vObj.id,request,vType="mailChange")

        if mobile:
            user.mobile = is_valid_mobile(mobile)
    except ValidationError as e:
        error_text = '; '.join(e.messages)
        return JsonResponse({'status': 'error', 'message': error_text}, status=400)

    # 2. Handle Avatar Logic
    if remove_avatar == 'true':
        # If user wants to delete the picture
        message+= "User Avatar Removed"
        user.remove_profile_picture()

    elif 'avatar' in request.FILES:
        # If user is uploading a new picture
        message+= "Changed User Avatar"
        user.profile = request.FILES['avatar']

    user.save()

    return JsonResponse({
        'status': 'success',
        'message': f'Done. {message}',
        'new_avatar_url': user.profile.url
    })


def blog(request):

    return render(request, "dashboard/blog.html")