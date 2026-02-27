from django.urls import path
from .consumers import *

websockets_urlpatterns = [
    path("ws/chats/<user_id>", ChatConsumer.as_asgi()),
    path("ws/status/",StatusConsumer.as_asgi()),
]
