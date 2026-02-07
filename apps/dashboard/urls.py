from django.urls import path
from apps.dashboard.views import *

urlpatterns = [
    path('', index, name='index'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/profile/', profile, name='profile'),
    path('dashboard/profile/update', profileUpdate, name='profileUpdate'),
    path('dashboard/seller/onboarding', sellerOnboarding, name='sellerOnboarding'),
    path('dashboard/seller/profile', sellerProfileView, name='sellerProfileView'),
    path('profile/seller/<uuid:seller_id>', sellerProfilePublicView, name='sellerProfilePublicView'),
    path('dashboard/seller/update', sellerProfileEdit, name='sellerProfileEdit'),
    path('logout/', logout, name='logout'),
    path('login/', login, name='login'),
    path('about/', about, name='about'),
    path('register/', register, name='register'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/<uuid:tokenId>/', reset_password, name='reset_password'),
    path('verify-mail/<uuid:tokenId>/', verifyNewMail, name='verify_new_mail'),
    path('blog/', blog, name='blog'),
    path('contact/', contact, name='contact'),
]