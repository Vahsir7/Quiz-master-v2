from flask import Blueprint, jsonify, request, current_app
from app.extension import db
from app.models import Admin, Attempt, Exam, Subject, Student
from app.decorators import token_required, roles_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard', methods=['GET'])
@token_required
@roles_required('admin')
def dashboard(current_user):
    try:
        #summary dashboard
        #total attempts per subject
        total_attempts = db.session.query(
            db.func.count(Attempt.AttemptID).label('total_attempts'),
            Subject.Name.label('subject_name')
        ).join(Exam).join(Subject).group_by(Subject.Name).all()
        
        #average score per subject
        average_scores = db.session.query(
            db.func.avg(Attempt.Score).label('average_score'),
            Subject.Name.label('subject_name')
        ).join(Exam).join(Subject).group_by(Subject.Name).all()

        #total exams created
        total_exams = db.session.query(
            db.func.count(Exam.ExamID).label('total_exams')
        ).all()

        #total students registered
        total_students = db.session.query(
            db.func.count(Student.StudentID).label('total_students')
        ).all()

        return jsonify({
            'total_attempts': [{'subject': row.subject_name, 'count': row.total_attempts} for row in total_attempts],
            'average_scores': [{'subject': row.subject_name, 'average_score': row.average_score} for row in average_scores],
            'total_exams': total_exams[0].total_exams if total_exams else 0,
            'total_students': total_students[0].total_students if total_students else 0
        }), 200
    
    except Exception as e:
        return jsonify({'message': 'Error fetching dashboard data', 'error': str(e)}), 500
