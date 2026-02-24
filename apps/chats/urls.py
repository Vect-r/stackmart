from django.urls import path
from .views import *


urlpatterns = [
    path('',chatsIndex,name="chats_dashboard"),
    path('<uuid:user_id>',chatsIndex,name='chat_conversation')
]