from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.db import models
from django.utils import timezone
from django.utils import timesince
from asgiref.sync import sync_to_async
import json
import zoneinfo
# from apps.users.models import *
from .models import *

@database_sync_to_async
def update_user_status_db(user, is_online):
    user.is_online = is_online
    if not is_online:
        user.last_seen = timezone.now()
    user.save()

@database_sync_to_async
def get_rendered_status_html(user_id):
    
    selected_user = get_object_or_404(User, id=user_id)
    return render_to_string(
        "chats/partials/user-status.html", 
        context={"user": selected_user}
    )

@database_sync_to_async
def get_rendered_status_circle_html(user_id):
    selected_user = get_object_or_404(User, id=user_id)
    return render_to_string(
        "chats/partials/chat-profile-status-indicator.html", 
        context={"user": selected_user}
    )

@database_sync_to_async
def get_user_conversation_ids(user):
    return list(Conversation.objects.filter(
        models.Q(user1=user) | models.Q(user2=user)
    ).values_list('id', flat=True))

@database_sync_to_async
def get_user_by_id(user_id):
    return get_object_or_404(User, id=user_id)

@database_sync_to_async
def get_or_create_conv_async(user, selected_user):
    return get_or_create_conversation(user, selected_user)

@database_sync_to_async
def create_message(content, sender, conversation):
    return Message.objects.create(
        body=content,
        sender=sender,
        conversation=conversation
    )

@database_sync_to_async
def mark_messages_read_db(conversation, current_user):
    # Update all unread messages sent by the OTHER user to read
    Message.objects.filter(conversation=conversation, is_read=False).exclude(sender=current_user).update(is_read=True)

@database_sync_to_async
def get_rendered_last_msg_html(conversation_id,current_user):
    conversation = Conversation.objects.get(id=conversation_id)
    return render_to_string('chats/partials/last-message.html',context={'conversation':conversation,'current_user':current_user})

@database_sync_to_async
def get_rendered_message_html(message_id, user):
    message = Message.objects.get(id=message_id)
    # Rendering templates might hit the DB to load related models, so it stays here
    return render_to_string("chats/partials/chat-pills-p.html", context={"msg": message, 'current_user': user})

# @database_sync_to_async
def get_rendered_read_receipt_html(message_id):
    message = Message.objects.get(id=message_id)
    return render_to_string("chats/partials/read-receipt.html",context={"msg":message})


class StatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        await self.channel_layer.group_add('global_man',self.channel_name)

        await self.accept()
        await self.update_status(True)

    async def disconnect(self, close_code):
        await self.update_status(False)
        await self.channel_layer.group_discard('global_man',self.channel_name)

    async def receive(self, text_data=None):
        data = json.loads(text_data)
        if 'is_active' in data:
            await self.update_status(data['is_active'])

    async def indicator_status_handler(self, event):
        # Change 'return' to 'await'
        circle_html = await get_rendered_status_circle_html(event['user_id'])
        await self.send(text_data=circle_html)

    async def last_message_handler(self,event):
        html = await get_rendered_last_msg_html(event['conversation_id'],self.user)
        await self.send(text_data=html)

    async def update_status(self, is_online):
        # 1. Update Database globally
        await update_user_status_db(self.user, is_online)

        # 2. Get all conversation IDs this user is a part of
        conversation_ids = await get_user_conversation_ids(self.user)

        # 3. Broadcast the status to all active chat rooms
        for conv_id in conversation_ids:
            await self.channel_layer.group_send(
                str(conv_id), {'type': 'status_handler','user_id': self.user.id,'status': is_online,'last_seen': self.user.last_seen,}
            )
            
        # 4. FIX: Broadcast to global_man (Must specify the group name!)
        await self.channel_layer.group_send(
            'global_man', 
            {'type': 'indicator_status_handler', 'user_id': self.user.id}
        )
            

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.other_user_id = self.scope["url_route"]["kwargs"]["user_id"]
        
        # Await our database helper functions
        selected_user = await get_user_by_id(self.other_user_id)
        self.conversation = await get_or_create_conv_async(self.user, selected_user)

        
        await mark_messages_read_db(self.conversation, self.user)

    
        # Native await for channel layer methods (no async_to_sync)
        await self.channel_layer.group_add(
            str(self.conversation.id), self.channel_name
        )

        await self.channel_layer.group_send(
           "global_man", {'type':"last_message_handler",'conversation_id':self.conversation.id}
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'conversation'):
            await self.channel_layer.group_discard(
                str(self.conversation.id), self.channel_name
            )

    async def receive(self, text_data=None):
        text_data_json = json.loads(text_data)
        content = text_data_json['body']

        # Await the message creation
        message = await create_message(content, self.user, self.conversation)
        
        event = {
            'type': 'message_handler',
            'message_id': message.id,
        }

        await self.channel_layer.group_send(
            str(self.conversation.id), event
        )

        await self.channel_layer.group_send(
           "global_man", {'type':"last_message_handler",'conversation_id':self.conversation.id}
        )

    async def message_handler(self, event):
        message_id = event['message_id']

        # 1. Grab timezone from WebSocket Cookies
        tzname = self.scope.get('local_tz')
        if tzname:
            try:
                timezone.activate(zoneinfo.ZoneInfo(tzname))
            except Exception:
                pass
        
        # Await the fetching and rendering of the HTML snippet
        html = await get_rendered_message_html(message_id, self.user)
        
        await self.send(text_data=html)
        
    async def status_handler(self, event):
        # HTMX intercept: Only update the UI if the event belongs to the OTHER user
        tzname = self.scope.get('local_tz')
        if tzname:
            try:
                timezone.activate(zoneinfo.ZoneInfo(tzname))
            except Exception:
                pass
        if event['user_id'] != self.user.id:    
            header_html = await get_rendered_status_html(event['user_id'])
            await self.send(text_data=header_html)
            
            