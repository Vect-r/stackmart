from rest_framework import serializers
from apps.users.models import Blog

class BlogListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ['id','title','summary','author']
