from functools import wraps
from flask import request, jsonify, current_app
import jwt
from .models import Admin, Student

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            if 'sub' in data:
                user_id = data['sub']
                user_type = data.get('type', 'student')
                if user_type == 'admin':
                    current_user = Admin.query.get(user_id)
                else:
                    current_user = Student.query.get(user_id) 
                if not current_user:
                    return jsonify({'message': 'User not found!'}), 404
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if current_user.role not in roles:
                return jsonify({'message': 'Access denied'}), 403
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator