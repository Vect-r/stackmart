from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from django.utils import timezone

from apps.master.middlewares.auth.utils import login_required_jwt
from .models import User, Conversation, Message, get_or_create_conversation
from .forms import SendMessageForm

# Create your views here.
def demo(request):
    return render(request,"chats/demo.html")

@login_required_jwt
def chatsIndex(request,user_id=None):
    current_user = request.authenticated_user
    form = SendMessageForm()
    conversations = Conversation.objects.filter(
        Q(user1=current_user) | Q(user2=current_user)
    ).select_related('user1','user2')

    selected_user = None
    messages = []
    conversation = None

    if request.method == "POST" and user_id:
        selected_user = get_object_or_404(User, id=user_id)
        conversation = get_or_create_conversation(current_user, selected_user)
        form = SendMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.authenticated_user
            message.receiver = selected_user
            message.conversation = conversation
            message.save()
            return render(request,'chats/partials/chat-pills.html',{'msg': message,'current_user':current_user})

    if user_id:
        selected_user = get_object_or_404(User, id=user_id)
        conversation = get_or_create_conversation(current_user, selected_user)
        receiver = get_object_or_404(User, id=user_id)

        messages = Message.objects.filter(
            conversation=conversation
        ).select_related('sender').order_by('created_at')

        for msg in messages:
            msg.local_date = timezone.localtime(msg.created_at).date()
        context={'selected_user':selected_user,'messages':messages,'current_user':current_user,'form':form}
        return render(request, 'chats/partials/conversation.html', context)

    context = {
        "conversations": conversations,
        "chat_messages": messages,
        "form":form,
        'user':request.authenticated_user
    }
    return render(request, "chats/chat.html", context)

    


    # if 'hx-request' in request.headers:
    #     context = {
    #         'target_user_id': user_id,
    #         # Mock data for UI demo
    #         'user_name': user_id.replace('_', ' ').title(), 
    #         'status': 'online',
    #     }       
    #     return render(request, 'chats/partials/conversation.html', context)
    return render(request,"chats/chat.html")