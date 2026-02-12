from django.urls import path
from apps.dashboard.views import *

urlpatterns = [
    path('', index, name='index'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/profile/', profile, name='profile'),
    path('dashboard/profile/update', profileUpdate, name='profileUpdate'),
    path('dashboard/seller/onboarding', sellerOnboarding, name='sellerOnboarding'),
    path('dashboard/seller/done', sellerOnboardingOutro, name='sellerOnboardingOutro'),
    path('dashboard/seller/profile', sellerProfileView, name='sellerProfileView'),
    path('profile/<uuid:user_id>', profilePublicView, name='profilePublicView'),
    path('profile/connect/<uuid:receiver_id>', sendRequest, name='sendRequest'),
    path('profile/accept/<uuid:sender_id>', accept_connection, name='accept_connection'),
    path('profile/connections/', connections, name='connections'),
    path('dashboard/seller/update', sellerProfileEdit, name='sellerProfileEdit'),
    path('logout/', logout, name='logout'),
    path('login/', login, name='login'),
    path('about/', about, name='about'),
    path('register/', register, name='register'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/<uuid:tokenId>/', reset_password, name='reset_password'),
    path('verify-mail/<uuid:tokenId>/', verifyNewMail, name='verify_new_mail'),
    path('blog/', blog, name='blog'),
    path('blog/create/', blogCreate, name="blogCreate"),
    path('blog/edit/<uuid:blog_id>', blogCreate, name="blogEdit"),
    path('api/blog/<uuid:blog_id>/upload/',upload_blog_image,name="uploadBlogImage"),
    path('contact/', contact, name='contact'),
]