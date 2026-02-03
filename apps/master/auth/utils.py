import jwt
from datetime import datetime, UTC, timedelta
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.hashers import make_password, check_password
from functools import wraps
from apps.users.models import User  # Your custom User model

# --- JWT LOGIC (Kept mostly the same) ---
def generate_token(user):
    payload = {
        'user_id': user.id,
        'user_type': getattr(user, 'user_type', 'user'), # Safe getattr in case field is missing
        'exp': datetime.now(UTC) + timedelta(days=1),
        'iat': datetime.now(UTC)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def hash_password(raw_password):
    return make_password(raw_password)

def verify_password(raw_password, hashed_password):
    return check_password(raw_password, hashed_password)

def decode_token(token):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except (jwt.ExpiredSignatureError, jwt.DecodeError):
        return None

# --- UPDATED DECORATOR (Using Session) ---
def login_required_jwt(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # CHANGE 1: Get token from Django Session, not Cookies
        token = request.session.get('access_token')
        
        if not token:
            return redirect('login') 
            
        payload = decode_token(token)
        
        # If token is invalid/expired, clear session and redirect
        if not payload:
            request.session.flush()
            return redirect('login')
            
        try:
            # CHANGE 2: Fetch user. 
            # Note: This hits the DB on every request. 
            # If performance is critical later, you can cache this.
            request.authenticated_user = User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            request.session.flush()
            return redirect('login')
            
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

def checkAuth(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # CHANGE 1: Get token from Django Session, not Cookies
        token = request.session.get('access_token')
        
        if not token:
            request.isAuthenticated=False
            return redirect('login') 
            
        payload = decode_token(token)
        
        # If token is invalid/expired, clear session and redirect
        if not payload:
            request.isAuthenticated=False
            request.session.flush()
            return redirect('login')
            
        # try:
        #     # CHANGE 2: Fetch user. 
        #     # Note: This hits the DB on every request. 
        #     # If performance is critical later, you can cache this.
        #     # userObj=User.objects.get(id=payload['user_id'])
        #     userObj = User.objects.filter(id=payload['user_id']).exists()
        #     if userObj:
        #         request.isAuthenticated=True

        # except User.DoesNotExist:
        #     request.session.flush()
        #     request.isAuthenticated=False
        #     return redirect('login')

        userObj = User.objects.filter(id=payload['user_id']).exists()
        if userObj:
            request.isAuthenticated=True
        else:
            request.session.flush()
            request.isAuthenticated=False
            return redirect('login')

            
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view