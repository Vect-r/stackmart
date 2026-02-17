
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from django_filters.rest_framework import DjangoFilterBackend

from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from apps.users.models import Blog, BlogImage

from .serializers import BlogListSerializer
from .pagination import *
from .filters import BlogFilter

from apps.master.auth.utils import login_required_jwt
# Create your views here.

class BlogListView(ListAPIView):
    queryset = Blog.objects.filter(status=Blog.Status.APPROVED).order_by('created_at')
    serializer_class = BlogListSerializer
    # pagination_class = BlogPagination
    pagination_class = ElidedPageNumberPagination

    filter_backends = [DjangoFilterBackend]
    filterset_class = BlogFilter

@api_view(['DELETE'])
@login_required_jwt
def delete_blog_image(request,blog_id,pk_id):
    if request.method=="DELETE":
        # image_url =request.query_params.get('image_url').lstrip('/media')
        get_image = get_object_or_404(BlogImage,pk=pk_id,blog__author=request.authenticated_user,blog__id=blog_id)
        get_image.delete()
        return Response({'message':'Deleted!!!'}, status=status.HTTP_200_OK)
    return Response({'message':'Error Occured'},status=status.HTTP_400_BAD_REQUEST)
    

@login_required_jwt
@api_view(['POST','DELETE'])
def blog_image_operations(request, blog_id,pk_id=None):
    if request.method == 'POST' and request.FILES.get('image'):
        blog = get_object_or_404(Blog, id=blog_id, author=request.authenticated_user)
        image_file = request.FILES['image']
        
        # Create the image object
        blog_image = BlogImage.objects.create(blog=blog, image=image_file)
        
        # Return the URL to the frontend
        return Response({
            'status': 'success',
            'url': blog_image.image.url,
            'pk_id': blog_image.pk,
            'filename': image_file.name
        },status=status.HTTP_200_OK)

    if request.method=="DELETE" and pk_id:
        # image_url =request.query_params.get('image_url').lstrip('/media')
        get_image = get_object_or_404(BlogImage,pk=pk_id,blog__author=request.authenticated_user,blog__id=blog_id)
        get_image.delete()
        return Response({'message':'Deleted!!!'}, status=status.HTTP_200_OK)
    return Response({'status': 'error', 'message': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)