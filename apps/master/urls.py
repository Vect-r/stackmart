from django.urls import path
from .views import *

urlpatterns = [
     path('blog',blog_list,name="demoBlogs"),
]