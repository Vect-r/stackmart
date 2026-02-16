from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import ModelViewSet
from apps.users.models import Blog
from .serializers import BlogListSerializer

class BlogPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

class ProductViewSet(ModelViewSet):
    queryset = Blog.objects.filter(status=Blog.STATUS.APPROVED)
    serializer_class = BlogListSerializer
    pagination_class = BlogPagination


# from rest_framework.pagination import PageNumberPagination
# from rest_framework.response import Response
# from django.core.paginator import Paginator

# class ElidedPageNumberPagination(PageNumberPagination):
#     page_size = 10

#     def get_paginated_response(self, data):
#         paginator = self.page.paginator
#         page_number = self.page.number

#         elided_range = paginator.get_elided_page_range(
#             number=page_number,
#             on_each_side=2,
#             on_ends=1
#         )

#         # return Response({
#         #     "count": paginator.count,
#         #     "next": self.get_next_link(),
#         #     "previous": self.get_previous_link(),
#         #     "current_page": page_number,
#         #     "total_pages": paginator.num_pages,
#         #     "page_range": list(elided_range),  # contains '…'
#         #     "results": data,
#         # })

#         #My own way to saw data

#         return Response({
#             'meta':{
#                 'count':paginator.count,
#                 'size':page_size
#             },
#             'results':data,
#             'pagination':{
#                 'next':self.get_next_link(),
#                 'previous':self.get_previous_link(),
#                 'current':page_number,
#             }
#         })
