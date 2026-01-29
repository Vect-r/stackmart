from django.shortcuts import render, redirect
from django.contrib import messages
from apps.master.utils.inputValidators import *
from apps.master.utils.hashings import hashIt
from apps.users.models import User
from django.views.decorators.cache import never_cache

# Create your views here.
def index(request):
    return render(request, "dashboard/index.html")

def login(request):
    return render(request, "dashboard/login.html")

def about(request):
    return render(request, "dashboard/about.html")

@never_cache
def register(request):
    if request.method=="POST":
        try:
            user_type_ = request.POST['user_type']
            pancard_ = request.FILES['pancard']
            email_ = is_valid_email(request.POST['email'])
            if User.objects.filter(email=email_).exists():
                messages.error(request, "Email already exists. Please Login or Reset Password")
                return redirect("register")
            mobile_ = is_valid_mobile(request.POST['mobile'])
            password_ = hashIt(validatePassword(match_password(request.POST['password'],request.POST['confirm_password'])))

            print(user_type_,pancard_,email_,mobile_,password_)
            new_user = User.objects.create(
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

def contact(request):
    return render(request, "dashboard/contact.html")

def forgot_password(request):
    return render(request, "dashboard/forgot_password.html")

def reset_password(request):
    return render(request, "dashboard/reset_password.html")

def blog(request):
    return render(request, "dashboard/blog.html")