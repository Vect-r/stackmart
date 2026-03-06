from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from django.utils import timezone

from apps.master.middlewares.auth.utils import login_required_jwt
from .models import User, Conversation, Message, get_or_create_conversation
from .forms import SendMessageForm
from django.http import JsonResponse, HttpResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

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



def chat_upload_image(request, user_id):
    if request.method == "POST":
        image = request.FILES.get('image')
        caption = request.POST.get('caption', '')
        # print(image,caption)
        # return HttpResponse("")
        
        if image:
            other_user = get_object_or_404(User, id=user_id)
            conversation = get_or_create_conversation(request.authenticated_user , other_user)
            
            # 1. Create the message in DB
            msg = Message.objects.create(
                conversation=conversation,
                sender=request.authenticated_user,
                type=Message.MessageType.IMG,
                image=image,
                body=caption
            )
            
            # 2. Broadcast to the open chat room via WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                str(conversation.id),
                {'type': 'message_handler', 'message_id': msg.id}
            )
            
            # 3. Broadcast to sidebars for unread count/previews
            async_to_sync(channel_layer.group_send)(
                "global_man",{'type': 'last_message_handler', 'conversation_id': conversation.id}
            )
            
    return HttpResponse("") # HTMX expects an empty response for hx-swap="none"
    
