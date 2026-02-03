from django.shortcuts import render, redirect
from django.contrib import messages
from apps.master.utils.inputValidators import *
from apps.master.auth.utils import *
from apps.users.models import User
from django.views.decorators.cache import never_cache

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
            messages.success(request,"Account Created Sucessfully...")
            return redirect('login')
        except ValidationError as e:
            messages.error(request, e)
            return redirect("register")
    return render(request, "dashboard/create_user.html")

def logout(request):
    request.session.flush()
    return redirect('index')

def contact(request):
    return render(request, "dashboard/contact.html")

def forgot_password(request):
    return render(request, "dashboard/forgot_password.html")

def reset_password(request):
    return render(request, "dashboard/reset_password.html")

def blog(request):
    return render(request, "dashboard/blog.html")