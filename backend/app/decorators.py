from functools import wraps
from flask import request, jsonify, current_app, g
import jwt
from .models import Admin, Student

def authentication(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                try:
                    token = request.headers['Authorization'].split(" ")[1]
                except IndexError:
                    return jsonify({'message': 'Malformed token header!'}), 400
            if not token:
                return jsonify({'message': 'Token is missing!'}), 401
            try:
                #print(f"Decoding token: {token}")
                #print(f"Using secret key: {current_app.config['SECRET_KEY']}")
                data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
                user_id = data['sub']
                user_type = data.get('type') 
                current_user = None
                if user_type == required_role:
                    if user_type == 'admin':
                        current_user = Admin.query.get(user_id)
                    elif user_type == 'student':
                        current_user = Student.query.get(user_id)
                    else:
                        return jsonify({'message': 'Cannot fetch user!'}), 404
                    #print(f"User found in database: {current_user}")
                else:
                    return jsonify({'message': 'Unauthorized user type!'}), 403
                if not current_user:
                    return jsonify({'message': 'User associated with token not found!'}), 404
                g = current_user
            except jwt.ExpiredSignatureError:
                #print("TOKEN ERROR: Expired signature.")
                return jsonify({'message': 'Token has expired!'}), 401
            except jwt.InvalidTokenError:
                #print("TOKEN ERROR: Invalid token. Secret key mismatch or malformed token.")
                return jsonify({'message': 'Invalid token!'}), 401
            #print(f"Current user: {current_user}")
            if not current_user:
                return jsonify({'message': 'User not found!'}), 404
            return f(*args, **kwargs)
        return decorated_function
    return decorator

