"""
Authentication Service
Handles Firebase token verification and user session management
"""
from firebase_admin import auth
from functools import wraps
from flask import request, jsonify
import jwt
import os
from datetime import datetime, timedelta


class AuthService:
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
    
    def verify_firebase_token(self, id_token):
        """Verify Firebase ID token"""
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            print(f'Token verification error: {e}')
            return None
    
    def create_session_token(self, user_id, email):
        """Create a session JWT token"""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_session_token(self, token):
        """Verify session JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user_info(self, user_id):
        """Get user information from Firebase"""
        try:
            user = auth.get_user(user_id)
            return {
                'uid': user.uid,
                'email': user.email,
                'displayName': user.display_name,
                'photoURL': user.photo_url,
                'emailVerified': user.email_verified
            }
        except Exception as e:
            print(f'Error getting user info: {e}')
            return None

    def update_user(self, uid, **kwargs):
        """Update user profile"""
        try:
            # Filter allowed fields
            allowed = ['email', 'display_name', 'photo_url', 'password', 'disabled']
            params = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
            
            if not params:
                return None
                
            user = auth.update_user(uid, **params)
            return {
                'uid': user.uid,
                'email': user.email,
                'displayName': user.display_name,
                'photoURL': user.photo_url
            }
        except Exception as e:
            print(f'Error updating user: {e}')
            raise e


def require_auth(f):
    """Decorator to require authentication for endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split(' ')[1]
            auth_service = AuthService()
            
            # Try Firebase token first
            decoded = auth_service.verify_firebase_token(token)
            if not decoded:
                # Try session token
                decoded = auth_service.verify_session_token(token)
            
            if not decoded:
                return jsonify({'error': 'Invalid token'}), 401
            
            # Add user info to request
            request.user = decoded
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function
