from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.master.utils.inputValidators import *
from apps.master.auth.utils import *
from apps.users.models import User, UserVerification, SellerProfile, Service, SocialLink, ConnectionRequest, Blog, BlogCategory, BlogImage
from django.views.decorators.cache import never_cache
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags
# from django.conf import settings
# from django.contrib.sites.shortcuts import get_current_site
from datetime import datetime, timedelta, UTC
from apps.users.forms import PasswordResetForm, BlogForm
from .mailings import MailSender
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
from django.utils import timezone
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.core import serializers
from apps.users.services import *
from django.http import Http404
import os


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
                
                print(hasattr(getUser,'seller_profile'))
                if getUser.user_type=="seller" and not hasattr(getUser,'seller_profile'):
                    print(True)
                    response = redirect('sellerOnboarding')
                else:
                    print(False)
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
        #     subject = 'Security Alert: Password Changed'
        #     html_message = render_to_string('dashboard/mails/password_reset_success.html', {
        #         'user': getUser,
        #     })
        #     plain_message = strip_tags(html_message)

        # # 3. Send the notification
        #     send_mail(
        #         subject,
        #         plain_message,
        #         settings.DEFAULT_FROM_EMAIL,
        #         [getUser.email],
        #         html_message=html_message,
        #         fail_silently=True, # Don't crash the user flow if mail fails
        #     )
            mailObj.sendPasswordReset(getUser)
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
    return render(request,'dashboard/profile.html',{'user':user,'isDefaultAvatar':isDefaultAvatar,'connection_count':getConnectionsCount(request.authenticated_user)})

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

@login_required_jwt
def sellerOnboardingOutro(request):
    return render(request,'dashboard/seller_onboarding_loader.html')

@login_required_jwt
def sellerOnboarding(request):
    context={}
    context['seller_type']={item[0]:item[1] for item in SellerProfile.SELLER_TYPE_CHOICES}
    context['social_media_platforms']={item[0]:item[1] for item in SocialLink.PLATFORM_CHOICES}
    context['service'] = Service.objects.filter(is_approved=True).all()

    if request.authenticated_user.user_type=="buyer" or hasattr(request.authenticated_user,'seller_profile'):
        raise Http404("Page Not Found")

    if request.method == "POST":
        entity_type_ = request.POST['entity_type']
        business_name_ = request.POST['business_name']
        address_ = request.POST['address']
        description_ = request.POST['description']
        services_list_ = request.POST['services_list']
        unavailable_list_ = request.POST['unavailable_list']
        socials_json_= request.POST['socials_json']

        user = request.authenticated_user


        #At First, We will add all the required fields.
        seller = SellerProfile(user=user,
                               seller_type=entity_type_,
                               business_name=business_name_,
                               description=description_,
                               address=address_)
        
        
        if 'profile_pic' in request.FILES:
            seller.profile_pic = request.FILES['profile_pic']

        seller.save()

        if services_list_:
            services_list_ = services_list_.split(',')
            # print(services_list_)
            objs = Service.objects.filter(name__in = services_list_,is_approved=True)
            print(objs)
            seller.services.add(*objs)

        if unavailable_list_:
            unavailable_list_ = unavailable_list_.split(',')
            serviceUnObjs=[]
            for i in unavailable_list_:
                try:
                    serviceUnObjs.append(Service.objects.create(name=i,suggested_by=seller))
                except IntegrityError:
                    pass
            seller.services.add(*serviceUnObjs)

        if socials_json_:
            socials_json_ = json.loads(socials_json_)
            # [{"platform":"linkedin","url":"https://google.com"}]

            for handle in socials_json_:
                SocialLink.objects.create(seller=seller,platform = handle['platform'],url = handle['url'])
            
        # seller.save()
        messages.success(request,"Business Profile Created.")
        return redirect('dashboard')
        print(entity_type_,business_name_,address_,description_,services_list_,unavailable_list_,socials_json_)


    return render(request, 'dashboard/seller_onboarding.html',context)

@login_required_jwt
def sellerProfileView(request):
    if request.authenticated_user.user_type=="buyer" or not hasattr(request.authenticated_user,'seller_profile'):
        raise Http404("Page Not Found.")

    # print(getConnections(request.authenticated_user).count())
    return render(request,'dashboard/seller_card.html',{'seller':request.authenticated_user.seller_profile,'connection_count':getConnectionsCount(request.authenticated_user)})

@login_required_jwt
def sendRequest(request,receiver_id):
    if request.authenticated_user.id == receiver_id:
        raise Http404('Page Not Found')
    else:
        receiver = get_object_or_404(User,id=receiver_id)
        send_connection_request(request.authenticated_user,receiver)

    
    
    return redirect('profilePublicView',user_id = receiver.id)

def profilePublicView(request,user_id):
    #1. First we will get User Object from id or else raise 404
    store={
            'seller':{'template_path':'dashboard/public_seller_profile.html'},
            'buyer':{'template_path':'dashboard/public_buyer_profile.html'},
        }

    getUser = get_object_or_404(User,id=user_id)
    context = {
        'existing_request':None,
        'next_url':request.path
    }

    if getUser.user_type=="seller" and hasattr(getUser,'seller_profile'):
        context['seller']=getUser.seller_profile
    else:
        context['buyer']=getUser

    #if current user is authenticated
    if request.isAuthenticated:
        #if profile's user is not same as current user
        if getUser.id!=request.authenticated_user.id:
            context['existing_request'] = getExistingRequest(request.authenticated_user,getUser.id)

    return render(request,store[getUser.user_type]['template_path'],context)

@login_required_jwt
def sellerProfileEdit(request):
    profile = get_object_or_404(SellerProfile, user=request.authenticated_user)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # --- A. Update Basic Fields ---
                profile.business_name = request.POST.get('business_name')
                profile.address = request.POST.get('address')
                profile.description = request.POST.get('description')
                
                # Handle Image Upload (Only update if a new file is sent)
                if 'profile_pic' in request.FILES:
                    profile.profile_pic = request.FILES['profile_pic']
                
                profile.save()

                # --- B. Sync Services ---
                # Get the comma-separated string from the hidden input
                services_str = request.POST.get('services_list', '')
                unavailable_str = request.POST.get('unavailable_list', '')
                
                # We will collect all valid Service objects here
                final_services = []

                # 1. Existing Approved Services
                if services_str:
                    names = [s.strip() for s in services_str.split(',') if s.strip()]
                    for name in names:
                        service_obj = Service.objects.filter(name__iexact=name).first()
                        if service_obj:
                            final_services.append(service_obj)

                # 2. Custom/New Services
                if unavailable_str:
                    new_names = [s.strip() for s in unavailable_str.split(',') if s.strip()]
                    for name in new_names:
                        service_obj, created = Service.objects.get_or_create(
                            name__iexact=name,
                            defaults={
                                'name': name,
                                'is_approved': False,
                                'suggested_by': profile
                            }
                        )
                        final_services.append(service_obj)
                
                # 3. Apply the sync (this adds new ones and removes unlisted ones)
                profile.services.set(final_services)


                # --- C. Sync Social Links ---
                socials_json = request.POST.get('socials_json')
                if socials_json:
                    # Strategy: Delete old links and recreate new ones (Cleanest for simple lists)
                    profile.social_links.all().delete()
                    
                    socials_data = json.loads(socials_json)
                    for item in socials_data:
                        if item.get('platform') and item.get('url'):
                            SocialLink.objects.create(
                                seller=profile,
                                platform=item.get('platform'),
                                url=item.get('url')
                            )

            messages.success(request, "Profile updated successfully.")
            return redirect('sellerProfileView') # Redirect back to the "Business Card" view

        except Exception as e:
            print(f"Error updating profile: {e}")
            messages.error(request, "An error occurred while saving changes.")

    # --- GET: PREPARE DATA FOR TEMPLATE ---
    
    # 1. Serialize User's Current Services for JS
    current_services = list(profile.services.values_list('name', flat=True))
    
    # 2. Serialize User's Current Socials for JS
    current_socials = [
        {'platform': link.platform, 'url': link.url} 
        for link in profile.social_links.all()
    ]

    # 3. Get All Approved Services for Autocomplete
    all_services = Service.objects.filter(is_approved=True).values_list('name', flat=True)

    context = {
        'seller': profile,
        'current_services_json': json.dumps(current_services),
        'current_socials_json': json.dumps(current_socials),
        'available_services_json': list(all_services),
        'social_media_platforms': {item[0]: item[1] for item in SocialLink.PLATFORM_CHOICES},
    }
    
    return render(request, 'dashboard/seller_edit.html', context)

@login_required_jwt
def connections(request):
    user = request.authenticated_user

    context={}
    context['active_connections'] = getConnections(user)
    context['pending_requests'] = getPendingConnections(user)
    # print(context['active_connections'])
    # print(context['pending_requests'])

    return render(request,'dashboard/connections.html',context)

@login_required_jwt
def accept_connection(request,sender_id):
    sender = User.objects.get(id = sender_id)
    connectionRequest = ConnectionRequest.objects.get(sender = sender,receiver = request.authenticated_user)
    connectionRequest.status = "accepted"
    connectionRequest.save()
    messages.success(request,f'You accepted {sender.username} request.')
    return redirect('connections')

def blog(request):

    return render(request, "dashboard/blog.html")

# def upload_blog_image(request, blog_id):
#     # ... checks ...
#     image_file = request.FILES['image']
    
#     # Django saves and renames here if necessary
#     blog_image = BlogImage.objects.create(blog=blog, image=image_file)
    
#     # Get the ACTUAL name on disk (e.g., "image_1.jpg")
#     actual_filename = os.path.basename(blog_image.image.name)

#     return JsonResponse({
#         'status': 'success',
#         'url': blog_image.image.url,
#         'filename': actual_filename # Send this instead of image_file.name
#     })

def upload_blog_image(request, blog_id):
    if request.method == 'POST' and request.FILES.get('image'):
        blog = get_object_or_404(Blog, id=blog_id, author=request.authenticated_user)
        image_file = request.FILES['image']
        
        # Create the image object
        blog_image = BlogImage.objects.create(blog=blog, image=image_file)
        
        # Return the URL to the frontend
        return JsonResponse({
            'status': 'success',
            'url': blog_image.image.url,
            'filename': image_file.name
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required_jwt
def blogCreate(request,blog_id=None):
    if request.method=="POST" and blog_id:
        blog = get_object_or_404(Blog,id=blog_id,author=request.authenticated_user)
        form = BlogForm(request.POST,request.FILES,instance=blog)
        if form.is_valid():
            blog_obj = form.save(commit=False)
            action = request.POST.get("status")
            if action == "submitted":
                blog_obj.status = Blog.Status.SUBMITTED

            blog_obj.save()
        else:
            print(form.errors)

    context={}
    
    if blog_id is None:
        blog=Blog.objects.create(author=request.authenticated_user)
        return redirect('blogEdit',blog_id=blog.id)

    context['categories'] = BlogCategory.objects.all()
    context['blog']= get_object_or_404(Blog,id=blog_id,author=request.authenticated_user,status="draft")
    return render(request,'dashboard/blog_create.html',context)


