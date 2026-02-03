from apps.master.auth.utils import decode_token
from apps.users.models import User

# def jwt_user_context(request):
#     """
#     Available in all templates as {{ current_user }}
#     """
#     # 1. If the decorator already ran, use that user object
#     if hasattr(request, 'authenticated_user'):
#         return {'current_user': request.authenticated_user}

#     # 2. If valid token exists in session (but view wasn't decorated)
#     #    we fetch the user so the Navbar still works.
#     token = request.session.get('access_token')
#     if token:
#         payload = decode_token(token)
#         if payload:
#             try:
#                 user = User.objects.get(id=payload['user_id'])
#                 return {'current_user': user}
#             except User.DoesNotExist:
#                 pass
    
#     # 3. No user logged in
#     return {'current_user': None}

def jwt_user_context(request):
    """
    Available in all templates as {{ is_authenticated }}
    """
    # 1. If the Middleware or Decorator already ran:
    # We check if the attribute exists and is not None.
    if hasattr(request, 'authenticated_user'):
        return {'isAuthenticated': request.authenticated_user is not None}

    # 2. Fallback: If Middleware didn't run, check session manually
    token = request.session.get('access_token')
    if token:
        payload = decode_token(token)
        if payload:
            # We use .filter().exists() because it is faster than .get()
            # since we don't need the actual user data, just confirmation they exist.
            user_exists = User.objects.filter(id=payload['user_id']).exists()
            return {'isAuthenticated': user_exists}
    
    # 3. Default: Not logged in
    return {'isAuthenticated': False}