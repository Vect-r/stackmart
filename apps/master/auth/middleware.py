from django.utils.deprecation import MiddlewareMixin
from .utils import decode_token
from apps.users.models import User

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Set default to None so the attribute ALWAYS exists
        request.isAuthenticated = False

        # 2. Check for token in session
        token = request.session.get('access_token')

        if token:
            payload = decode_token(token)
            if payload:

                #this is very long

                # try:
                #     # 3. Attach user if token is valid
                #     request.authenticated_user = User.objects.get(id=payload['user_id'])
                #     request.isAuthenticated = User.objects.filter(id=payload['user_id']).exists()
                # except User.DoesNotExist:
                #     # Token valid but user deleted? Clear session.
                #     request.session.flush()

                #this is short
                request.isAuthenticated = User.objects.filter(id=payload['user_id']).exists()
                if not request.isAuthenticated:
                    request.session.flush()
                
        response = self.get_response(request)
        return response