# apps/master/auth/channels_middleware.py
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from django.contrib.sessions.models import Session
from django.utils import timezone
from asgiref.sync import sync_to_async

from apps.users.models import User
from .utils import decode_token


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        scope["user"] = None

        headers = dict(scope["headers"])
        # print(headers)
        cookies = headers.get(b"cookie", b"").decode()

        session_key = None
        for part in cookies.split(";"):
            if "sessionid=" in part:
                session_key = part.split("=")[1].strip()


        if session_key:
            session = await sync_to_async(Session.objects.get)(session_key=session_key)
            session_data = session.get_decoded()

            token = session_data.get("access_token")
            if token:
                payload = decode_token(token)
                if payload:
                    try:
                        user = await sync_to_async(User.objects.get)(id=payload["user_id"])
                        scope["user"] = user
                    except User.DoesNotExist:
                        scope["user"] = None

        return await super().__call__(scope, receive, send)