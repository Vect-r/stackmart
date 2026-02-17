from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.request import Request
from apps.api.views import BlogListView

#For testing purpose only.
#This will be deprecated in future and deleted.

def blog_list(request):
    drf_request = Request(request)  # 🔥 wrap it

    view = BlogListView()
    view.request = drf_request

    queryset = view.filter_queryset(view.get_queryset())
    page = view.paginate_queryset(queryset)
    serializer = view.get_serializer(page, many=True)

    paginated_response = view.get_paginated_response(serializer.data)
    data = paginated_response.data

    context = {
        "results": data["results"],
        "meta": data["meta"],
        "pagination": data["pagination"],
    }

    if request.headers.get("HX-Request"):
        return render(request, "partials/blog_list.html", context)

    return render(request, "blog_list.html", context)
