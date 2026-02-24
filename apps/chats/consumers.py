from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.template.loader import render_to_string
import json
from apps.users.models import *
from django.shortcuts import get_object_or_404
from .models import Message,get_or_create_conversation


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        self.other_user_id = self.scope["url_route"]["kwargs"]["user_id"]
        selected_user = get_object_or_404(User, id=self.other_user_id)
        self.conversation = get_or_create_conversation(self.user, selected_user)
        # print(self.conversation)
        async_to_sync(self.channel_layer.group_add)(
            self.conversation.id, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.conversation.id,self.channel_name
        )

    def receive(self, text_data = None,):
        text_data_json = json.loads(text_data)
        body = text_data_json['body']

        message = Message.objects.create(
            body = body,
            sender = self.user,
            conversation = self.conversation
        )
        
        event = {
            'type':'message_handler',
            'message_id':message.id,
        }

        async_to_sync(self.channel_layer.group_send)(
            self.conversation.id,event
        )

    def message_handler(self,event):
        message_id=event['message_id']
        message = Message.objects.get(id=message_id)
        html = render_to_string("chats/partials/chat-pills-p.html",context={"msg":message,'current_user':self.user,'selected_user':get_object_or_404(User,id=self.other_user_id)})
        self.send(text_data=html)
