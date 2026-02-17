
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
# Create your views here.

@api_view(['GET'])
def getCurrentUserDraftBlogs(request):
    pass

def getCurrentUserSubmittedBlogs(request):
    pass

# @api_view(['GET'])
# def getBlogs(request):
#     querySet = Blog.objects.all()
#     serializer = BlogListSerializer(querySet, many=True)
#     context = {'meta':{'total':querySet.count()},'results':serializer.data}
#     return Response(context, status=status.HTTP_200_OK)

class BlogListView(ListAPIView):
    queryset = Blog.objects.all().order_by('created_at')
    serializer_class = BlogListSerializer
    # pagination_class = BlogPagination
    pagination_class = ElidedPageNumberPagination

    filter_backends = [DjangoFilterBackend]
    filterset_class = BlogFilter
    

def upload_blog_image(request, blog_id):
    if request.method == 'POST' and request.FILES.get('image'):
        blog = get_object_or_404(Blog, id=blog_id, author=request.authenticated_user)
        image_file = request.FILES['image']
        
        # Create the image object
        blog_image = BlogImage.objects.create(blog=blog, image=image_file)
        
        # Return the URL to the frontend
        return JsonResponse({
            'status': 'success',
            'url': blog_image.image.url,
            'filename': image_file.name
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

