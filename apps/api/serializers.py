from rest_framework import serializers
from apps.users.models import Blog, User, BlogCategory

class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['name','slug']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','id','profile']

class BlogListSerializer(serializers.ModelSerializer):
    author  = AuthorSerializer()
    category = BlogCategorySerializer()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %z")
    class Meta:
        model = Blog
        fields = ['id','title','created_at','category','summary','author']