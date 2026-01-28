from django.urls import path
from apps.dashboard.views import *

urlpatterns = [
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('about/', about, name='about'),
    path('register/', register, name='register'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/', reset_password, name='reset_password'),
    path('blog/', blog, name='blog'),
    path('contact/', contact, name='contact'),
]