from django.urls import path
from .views import *


urlpatterns = [
    path('blogs/', BlogListView.as_view(), name='blog-list'),
    path('blog/<uuid:blog_id>/image/upload/',blog_image_operations ,name="uploadBlogImage"),
    path('blog/<uuid:blog_id>/image/delete/<int:pk_id>', blog_image_operations, name='deleteBlogImage'),
]