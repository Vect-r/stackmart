from django.urls import path
from .views import *

urlpatterns = [
    path('api/blog/<uuid:blog_id>/upload/',upload_blog_image,name="uploadBlogImage"),
]