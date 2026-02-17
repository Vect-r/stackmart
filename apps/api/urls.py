from django.urls import path
from .views import *


urlpatterns = [
    path('blog/<uuid:blog_id>/upload/',upload_blog_image,name="uploadBlogImage"),
    path('blogs/', BlogListView.as_view(), name='blog-list'),
    path('blog/image/delete/<int:pk_id>', delete_blog_image, name='deleteBlogImage'),
]