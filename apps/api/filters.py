import django_filters
from apps.users.models import Blog


class BlogFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    author = django_filters.CharFilter(
        field_name='author__username',
        lookup_expr='icontains'
    )
    category = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact'
    )

    class Meta:
        model = Blog
        fields = ['title', 'author', 'category']

class UserBlogFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact'
    )
    status = django_filters.ChoiceFilter(choices = Blog.Status.choices)

    class Meta:
        model = Blog
        fields = ['title', 'author', 'category','status']
