from django.shortcuts import render
from apps.users.models import Blog, BlogImage
from django.http import JsonResponse
from rest_framework.decorators import api_view

# Create your views here.

@api_view(['GET'])
def getCurrentUserDraftBlogs(request):
    pass

def getCurrentUserSubmittedBlogs(request):
    pass

@api_view(['GET'])
def getBlogs(request):
    pass


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

