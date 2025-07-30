from flask import Blueprint, jsonify, request, current_app
from app.extension import db, cache
from app.models import Admin, Attempt, Exam, Subject, Student, Chapter, Question
from app.decorators import authentication
from datetime import datetime
from app.celery_tasks import send_daily_reminders, generate_monthly_report, send_new_exam_notification


admin_bp = Blueprint('admin', __name__)

@authentication('admin')
@admin_bp.route('/dashboard', methods=['GET'])
def dashboard():
    try:
        # Total attempts per subject
        total_attempts = db.session.query(
            db.func.count(Attempt.AttemptID).label('total_attempts'),
            Subject.SubjectName.label('subject_name')
        ).join(Attempt.exam) \
         .join(Exam.chapter) \
         .join(Chapter.subject) \
         .group_by(Subject.SubjectName).all()

        # Average score per subject
        average_scores = db.session.query(
            db.func.avg(Attempt.Marks).label('average_score'),
            Subject.SubjectName.label('subject_name')
        ).join(Attempt.exam) \
         .join(Exam.chapter) \
         .join(Chapter.subject) \
         .group_by(Subject.SubjectName).all()

        # Total exams created
        total_exams = db.session.query(
            db.func.count(Exam.ExamID)
        ).scalar()

        # Total students registered
        total_students = db.session.query(
            db.func.count(Student.StudentID)
        ).scalar()

        return jsonify({
            'total_attempts': [{'subject': row.subject_name, 'count': row.total_attempts} for row in total_attempts],
            'average_scores': [{'subject': row.subject_name, 'average_score': row.average_score} for row in average_scores],
            'total_exams': total_exams or 0,
            'total_students': total_students or 0
        }), 200

    except Exception as e:
        return jsonify({'message': 'Error fetching dashboard data', 'error': str(e)}), 500

# Student
@authentication('admin')
@admin_bp.route('/students', methods=['GET'])
def get_students():
    try:
        student_id = request.args.get('student_id', type=int)
        search = request.args.get('search', type=str)
        if student_id:
            # GET /admin/students?student_id={{id}}
            student = Student.query.get(student_id)
            if not student:
                return jsonify({'message': 'Student not found'}), 404
            return jsonify({
                'StudentID': student.StudentID,
                'Name': student.Name,
                'Email': student.Email,
                'DOB': student.DOB.strftime("%Y-%m-%d"),
                'CollegeName': student.CollegeName,
                'Degree': student.Degree
            }), 200
        else:
            query = Student.query
            if search:
                query = query.filter(Student.Name.ilike(f'%{search}%'))
            students = query.all()
            return jsonify([{'StudentID': student.StudentID,
                            'Name': student.Name,
                            'Email': student.Email}
                            for student in students]), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching students', 'error': str(e)}), 500

@authentication('admin')
@admin_bp.route('/students', methods=['DELETE'])
def delete_student():
    try:
        student_id = request.args.get('student_id', type=int)
        if not student_id:
            return jsonify({'message': 'student_id query parameter is required to delete a student'}), 400
        # DELETE /admin/students?student_id={{id}}
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'message': 'Student not found'}), 404
        db.session.delete(student)
        db.session.commit()
        cache.clear()
        return jsonify({'message': 'Student deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting student', 'error': str(e)}), 500


## Subject CRUD

@authentication('admin')
@admin_bp.route('/subjects', methods=['POST'])
def create_subject():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid input'}), 400
    try:
        subject_name = data.get('SubjectName')
        description = data.get('Description', '')
        if Subject.query.filter_by(SubjectName=subject_name).first():
            return jsonify({'message': 'A subject with this name already exists'}), 409
        new_subject = Subject(SubjectName=subject_name, Description=description)
        db.session.add(new_subject)
        db.session.commit()
        cache.clear()
        return jsonify({'message': 'Subject created successfully', 'subject_id': new_subject.SubjectID}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating subject', 'error': str(e)}), 500

@authentication('admin')
@admin_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
def update_subject(subject_id):
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid input'}), 400
    try:
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'message': 'Subject not found'}), 404
        subject.SubjectName = data.get('SubjectName', subject.SubjectName)
        subject.Description = data.get('Description', subject.Description)
        db.session.commit()
        cache.clear()
        return jsonify({'message': 'Subject updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating subject', 'error': str(e)}), 500

@authentication('admin')
@admin_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    try:
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'message': 'Subject not found'}), 404
        db.session.delete(subject)
        db.session.commit()
        cache.clear()
        return jsonify({'message': 'Subject deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting subject', 'error': str(e)}), 500

@authentication('admin')
@admin_bp.route('/subjects', methods=['GET'])
@cache.cached(timeout=300)
def get_subjects():
    try:
        search = request.args.get('search', type=str)
        query = Subject.query
        if search:
            query = query.filter(Subject.SubjectName.ilike(f'%{search}%'))
        subjects = query.all()
        return jsonify([{'SubjectID': subject.SubjectID,
                         'SubjectName': subject.SubjectName,
                         'Description': subject.Description}
                          for subject in subjects]), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching subjects', 'error': str(e)}), 500

#Chapter CRUD

@authentication('admin')
@admin_bp.route('/subjects/<int:subject_id>/chapters', methods=['POST'])
def create_chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if not subject:
        return jsonify({'message': 'Subject not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid input'}), 400
    try:
        chapter_name = data.get('ChapterName')
        description = data.get('Description', '')

        if Chapter.query.filter_by(ChapterName=chapter_name, SubjectID=subject_id).first():
            return jsonify({'message': 'A chapter with this name already exists for the subject'}), 409

        new_chapter = Chapter(SubjectID=subject_id,
                              ChapterName=chapter_name,
                              Description=description)
        db.session.add(new_chapter)
        db.session.commit()
        cache.clear()
        return jsonify({'message': 'Chapter created successfully', 'chapter_id': new_chapter.ChapterID}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating chapter', 'error': str(e)}), 500

@authentication('admin')
@admin_bp.route('/subjects/<int:subject_id>/chapters', methods=['GET'])
@cache.cached(timeout=300)
def get_chapters(subject_id):
    try:
        search = request.args.get('search', type=str)
        query = Chapter.query.filter_by(SubjectID=subject_id)
        if search:
            query = query.filter(Chapter.ChapterName.ilike(f'%{search}%'))
        chapters = query.all()
        return jsonify([{'ChapterID': chapter.ChapterID,
                         'ChapterName': chapter.ChapterName,
                         'Description': chapter.Description,
                         'SubjectID': chapter.SubjectID}
                          for chapter in chapters]), 200

    except Exception as e:
        return jsonify({'message': 'Error fetching chapters', 'error': str(e)}), 500

@authentication('admin')
@admin_bp.route('/chapters/<int:chapter_id>', methods=['PUT'])
def update_chapter(chapter_id):
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid input'}), 400
    try:
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return jsonify({'message': 'Chapter not found'}), 404

        chapter.ChapterName = data.get('ChapterName', chapter.ChapterName)
        chapter.Description = data.get('Description', chapter.Description)
        db.session.commit()
        cache.clear()
        return jsonify({'message': 'Chapter updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating chapter', 'error': str(e)}), 500

@authentication('admin')
@admin_bp.route('/chapters/<int:chapter_id>', methods=['DELETE'])
def delete_chapter(chapter_id):
    try:
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return jsonify({'message': 'Chapter not found'}), 404
        db.session.delete(chapter)
        db.session.commit()
        cache.clear()
        return jsonify({'message': 'Chapter deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting chapter', 'error': str(e)}), 500

#exams CRUD
@authentication('admin')
@admin_bp.route('/exams/<int:exam_id>/publish', methods=['PUT'])
def publish_exam(exam_id):
    try:
        exam = Exam.query.get(exam_id)
        if not exam:
            return jsonify({'message': 'Exam not found'}), 404
        
        exam.Published = not exam.Published
        
        # If the exam is being published, trigger the notification task
        if exam.Published:
            send_new_exam_notification.delay(exam.ExamID)
            
        db.session.commit()
        cache.clear()
        
        return jsonify({
            'message': f'Exam has been {"published" if exam.Published else "unpublished"}.',
            'published_status': exam.Published
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating exam status', 'error': str(e)}), 500

@authentication('admin')
@admin_bp.route('/exams', methods=['GET'])
@cache.cached(timeout=300)
def get_exam():
    try:
        chapter_id = request.args.get('chapter_id', type=int)
        subject_id = request.args.get('subject_id', type=int)
        search = request.args.get('search', type=str)

        query = db.session.query(
            Exam,
            Chapter.ChapterName,
            Subject.SubjectName,
            Chapter.SubjectID
        ).join(Exam.chapter).join(Chapter.subject)

        if subject_id:
            query = query.filter(Chapter.SubjectID == subject_id)
        if chapter_id:
            query = query.filter(Exam.ChapterID == chapter_id)
        if search:
            query = query.filter(Exam.ExamName.ilike(f'%{search}%'))

        all_exams = query.all()

        result = []
        for exam, chapter_name, subject_name, subject_id_val in all_exams:
            result.append({
                'ExamID': exam.ExamID,
                'ExamName': exam.ExamName,
                'TotalQuestions': exam.TotalQuestions,
                'TotalDuration': exam.TotalDuration,
                'ExamDate': exam.ExamDate.strftime("%Y-%m-%d"),
                'ChapterID': exam.ChapterID,
                'ChapterName': chapter_name,
                'SubjectID': subject_id_val,
                'SubjectName': subject_name,
                'Published': exam.Published,
                'ExamType': exam.ExamType,
                'StartTime': exam.StartTime.strftime("%H:%M") if exam.StartTime else None
            })
        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching exams: {e}", exc_info=True)
        return jsonify({'message': 'Error fetching exams', 'error': str(e)}), 500

@authentication('admin')
@admin_bp.route('/exams', methods=['POST'])
def create_exam():
    chapter_id = request.args.get('chapter_id', type=int)
    if not chapter_id:
        return jsonify({'message': 'chapter_id query parameter is required to create an exam'}), 400

    data = request.get_json()
    if not Chapter.query.get(chapter_id):
        return jsonify({'message': 'Chapter not found'}), 404

    try:
        start_time = None
        exam_date = datetime.strptime(data.get('ExamDate'), "%Y-%m-%d")

        if data.get('ExamType') == 'specific_time' and data.get('StartTime'):
            start_time = datetime.strptime(f"{data.get('ExamDate')} {data.get('StartTime')}", "%Y-%m-%d %H:%M")

        new_exam = Exam(
            ChapterID=chapter_id,
            ExamName=data.get('ExamName'),
            TotalMarks=0,
            TotalQuestions=0,
            TotalDuration=int(data.get('TotalDuration', 0)),
            ExamDate=exam_date,
            Published=data.get('Published', False),
            ExamType=data.get('ExamType', 'deadline'),
            StartTime=start_time
        )
        db.session.add(new_exam)
        db.session.commit()
        cache.clear()
        return jsonify({'message': 'Exam created successfully', 'exam_id': new_exam.ExamID}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating exam', 'error': str(e)}), 500

@authentication('admin')
@admin_bp.route('/exams/<int:exam_id>', methods=['PUT'])
def update_exam(exam_id):
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid input'}), 400
    try:
        exam = Exam.query.get(exam_id)
        if not exam:
            return jsonify({'message': 'Exam not found'}), 404

        if exam.Published:
            return jsonify({'message': 'Cannot update a published exam'}), 403

        exam.ExamName = data.get('ExamName', exam.ExamName)
        exam.TotalDuration = data.get('TotalDuration', exam.TotalDuration)
        
        if 'ExamDate' in data:
            exam.ExamDate = datetime.strptime(data['ExamDate'], "%Y-%m-%d")

        exam.Published = data.get('Published', exam.Published)
        exam.ExamType = data.get('ExamType', exam.ExamType)

        if exam.ExamType == 'specific_time':
            if 'StartTime' in data and data['StartTime']:
                exam_date_str = exam.ExamDate.strftime('%Y-%m-%d')
                exam.StartTime = datetime.strptime(f"{exam_date_str} {data['StartTime']}", "%Y-%m-%d %H:%M")
        else:
            exam.StartTime = None

        db.session.commit()
        cache.clear()
        return jsonify({'message': 'Exam updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating exam', 'error': str(e)}), 500
        
@authentication('admin')
@admin_bp.route('/exams/<int:exam_id>', methods=['DELETE'])
def delete_exam(exam_id):
    try:
        exam = Exam.query.get(exam_id)
        if not exam:
            return jsonify({'message': 'Exam not found'}), 404
        db.session.delete(exam)
        db.session.commit()
        cache.clear()
        return jsonify({'message': 'Exam deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting exam', 'error': str(e)}), 500

#questions CRUD

@authentication('admin')
@admin_bp.route('/exams/<int:exam_id>/questions', methods=['POST'])
def create_question(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    if exam.Published:
        return jsonify({'message': 'Cannot add questions to a published exam'}), 403
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid input'}), 400
    try:
        question_statement = data.get('QuestionStatement')
        option1 = data.get('Option1')
        option2 = data.get('Option2')
        option3 = data.get('Option3', '')
        option4 = data.get('Option4', '')
        correct_option = data.get('CorrectOption')
        marks = data.get('Marks', 0)
        negative_marks = data.get('NegMarks', 0)

        new_question = Question(ExamID=exam_id,
                                QuestionStatement=question_statement,
                                Option1=option1,
                                Option2=option2,
                                Option3=option3,
                                Option4=option4,
                                CorrectOption=correct_option,
                                Marks=marks,
                                NegMarks=negative_marks)
        db.session.add(new_question)
        exam.TotalQuestions += 1
        exam.TotalMarks += marks
        db.session.commit()
        cache.clear()
        return jsonify({'message': 'Question created successfully', 'question_id': new_question.QuestionID}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating question', 'error': str(e)}), 500

@authentication('admin')
@admin_bp.route('/exams/<int:exam_id>/questions', methods=['GET'])
@cache.cached(timeout=300)
def get_questions(exam_id):
    try:
        questions = Question.query.filter_by(ExamID=exam_id).all()
        return jsonify([{'QuestionID': question.QuestionID,
                         'ExamID': question.ExamID,
                         'QuestionStatement': question.QuestionStatement,
                         'Option1': question.Option1,
                         'Option2': question.Option2,
                         'Option3': question.Option3,
                         'Option4': question.Option4,
                         'CorrectOption': question.CorrectOption,
                         'Marks': question.Marks,
                         'NegMarks': question.NegMarks}
                          for question in questions]), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching questions', 'error': str(e)}), 500

@authentication('admin')
@admin_bp.route('/questions/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid input'}), 400
    try:
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'message': 'Question not found'}), 404
        
        exam = Exam.query.get(question.ExamID)
        if exam.Published:
            return jsonify({'message': 'Cannot update questions of a published exam'}), 403

        question.QuestionStatement = data.get('QuestionStatement', question.QuestionStatement)
        question.Option1 = data.get('Option1', question.Option1)
        question.Option2 = data.get('Option2', question.Option2)
        question.Option3 = data.get('Option3', question.Option3)
        question.Option4 = data.get('Option4', question.Option4)
        question.CorrectOption = data.get('CorrectOption', question.CorrectOption)
        exam.TotalMarks = (exam.TotalMarks - question.Marks) + data.get('Marks', question.Marks)
        question.Marks = data.get('Marks', question.Marks)
        question.NegMarks = data.get('NegMarks', question.NegMarks)

        db.session.commit()
        cache.clear()
        return jsonify({'message': 'Question updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating question', 'error': str(e)}), 500

@authentication('admin')
@admin_bp.route('/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    try:
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'message': 'Question not found'}), 404
            
        exam = Exam.query.get(question.ExamID)
        if exam.Published:
            return jsonify({'message': 'Cannot delete questions of a published exam'}), 403

        exam.TotalQuestions -= 1
        exam.TotalMarks -= question.Marks
        db.session.delete(question)
        db.session.commit()
        cache.clear()
        return jsonify({'message': 'Question deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting question', 'error': str(e)}), 500
    
#celery tasks
@authentication('admin')
@admin_bp.route('/students/<int:student_id>/send-report', methods=['POST'])
def send_exam_report(student_id):
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'message': 'Student not found'}), 404

        print(student)
        from app.celery_tasks import generate_exam_report_for_student
        generate_exam_report_for_student.delay(student_id)

        return jsonify({'message': 'Exam report generation has been triggered.'}), 202
    except Exception as e:
        print(f"Error triggering report generation: {e}")
        return jsonify({'message': 'Error triggering report generation', 'error': str(e)}), 500

@authentication('admin')
@admin_bp.route('/students/export', methods=['POST'])
def export_students():
    """
    Triggers an asynchronous export of all students' data.
    """
    try:
        from app.celery_tasks import export_all_student_reports
        export_all_student_reports.delay()
        return jsonify({'message': 'All students data is being exported and will be sent to your email.'}), 202
    except Exception as e:
        return jsonify({'message': 'Error triggering export', 'error': str(e)}), 500