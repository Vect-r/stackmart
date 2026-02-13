from django.shortcuts import render, redirect, get_list_or_404
from apps.master.auth.utils import login_required_jwt, checkAuth

# Create your views here.
@login_required_jwt
def chatsIndex(request):
    return render(request,"chats/chat.html")