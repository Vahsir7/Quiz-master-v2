from flask import Blueprint, jsonify, request, current_app
from app.extension import db
from app.models import Admin, Attempt, Exam, Subject, Student
from app.decorators import token_required, roles_required
from datetime import datetime

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard', methods=['GET'])
@token_required
@roles_required('student')
def dashboard(current_user):
    try:
        # Fetch student-specific data
        # Total attempts per subject
        total_attempts = db.session.query(
            db.func.count(Attempt.AttemptID).label('total_attempts'),
            Subject.Name.label('subject_name')
        ).join(Exam).join(Subject).filter(Attempt.StudentID == current_user.StudentID).group_by(Subject.Name).all()
        
        # Average score per subject
        average_scores = db.session.query(
            db.func.avg(Attempt.Score).label('average_score'),
            Subject.Name.label('subject_name')
        ).join(Exam).join(Subject).filter(Attempt.StudentID == current_user.StudentID).group_by(Subject.Name).all()

        #total exams taken
        total_exams = db.session.query(
            db.func.count(Exam.ExamID).label('total_exams')
        ).join(Attempt).filter(Attempt.StudentID == current_user.StudentID).all()

        #average score across all exams
        average_score = db.session.query(
            db.func.avg(Attempt.Score).label('average_score')
        ).filter(Attempt.StudentID == current_user.StudentID).scalar()
        if average_score is None:
            average_score = 0

        return jsonify({
            'total_attempts': [{'subject': row.subject_name, 'count': row.total_attempts} for row in total_attempts],
            'average_scores': [{'subject': row.subject_name, 'average_score': row.average_score} for row in average_scores],
            'average_score': average_score,
            'total_exams': total_exams[0].total_exams if total_exams else 0
        }), 200
    
    except Exception as e:
        return jsonify({'message': 'Error fetching dashboard data', 'error': str(e)}), 500
    
@student_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if Student.query.filter_by(Email=data.get('email')).first():
        return jsonify({'message': 'An account with this email already exists'}), 409 
    try:
        student = Student(
            Name=data.get('name'),
            Email=data.get('email'),
            #PasswordHash=data.get('password'),
            DOB=datetime.strptime(data.get('dob'), '%Y-%m-%d'),
            CollegeName=data.get('college_name'),
            Degree=data.get('degree'),
        )
        password = data.get('password')
        student.set_password(password)
        db.session.add(student)
        db.session.commit()
        return jsonify({'message': 'Student registered successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error registering student', 'error': str(e)}), 500

