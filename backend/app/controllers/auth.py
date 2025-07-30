from flask import request, jsonify, Blueprint, current_app
from app.extension import bcrypt
from app.models import Admin, Student
import jwt
import datetime


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    #print(data)
    login_type = data.get('type')
    email = data.get('email')
    password = data.get('password')
    #print(f"Login type: {login_type}, Email: {email}, Password: {password}")
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400
    
    if login_type == 'admin':
        admin = Admin.query.filter_by(Email=email).first()
        #print(admin)
        if not admin:
            return jsonify({'message': 'Admin not found'}), 404
        #print(admin.PasswordHash, password)
        if admin and bcrypt.check_password_hash(admin.PasswordHash, password):
            print("Admin authenticated")
            #key = current_app.config['SECRET_KEY']
            #print(f"\n>>> ENCODING KEY: '{key}' | TYPE: {type(key)} | LENGTH: {len(key)}\n")
            token = jwt.encode({
                'sub': admin.AdminID,
                'type': 'admin',
                'exp': datetime.datetime.now() + datetime.timedelta(hours=1)
            }, current_app.config['SECRET_KEY'], algorithm='HS256')
            #print(f"Generated token: {token}")
            return jsonify({'token': token, "message": "Admin authenticated"}), 200
        
    else:
        student = Student.query.filter_by(Email=email).first()
        if not student:
            return jsonify({'message': 'Invalid credentials'}), 401
        if student and bcrypt.check_password_hash(student.PasswordHash, password):
            token = jwt.encode({
                'sub': student.StudentID,
                'type': 'student',
                'exp': datetime.datetime.now() + datetime.timedelta(hours=1)
            }, current_app.config['SECRET_KEY'], algorithm='HS256')
            return jsonify({
                'token': token, 
                "message": "Student authenticated",
                "student_id": student.StudentID
            }), 200
        
    return jsonify({'message': 'Invalid credentials'}), 401

