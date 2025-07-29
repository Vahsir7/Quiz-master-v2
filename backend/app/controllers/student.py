from flask import Blueprint, jsonify, request
from app.extension import db
from app.models import Attempt, Exam, Subject, Student, Chapter, SelectedAnswer
from app.decorators import authentication
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import desc

student_bp = Blueprint('student', __name__)


@authentication('student')
@student_bp.route('/<int:student_id>/dashboard', methods=['GET'])
def dashboard(student_id):
    try:
        # Total attempts and average scores per subject
        total_attempts = db.session.query(
            db.func.count(Attempt.AttemptID).label('total_attempts'),
            Subject.SubjectName.label('subject_name')
        ).join(Attempt.exam).join(Exam.chapter).join(Chapter.subject).filter(Attempt.StudentID == student_id).group_by(Subject.SubjectName).all()

        # Average Scores per Subject
        average_scores = db.session.query(
            db.func.avg(Attempt.Marks).label('average_score'),
            Subject.SubjectName.label('subject_name')
        ).join(Attempt.exam).join(Exam.chapter).join(Chapter.subject).filter(Attempt.StudentID == student_id).group_by(Subject.SubjectName).all()

        # Total Exams Attempted
        total_exams = db.session.query(
            db.func.count(Attempt.AttemptID)
        ).filter(Attempt.StudentID == student_id).scalar()

        # Average Score across all attempts
        average_score = db.session.query(
            db.func.avg(Attempt.Marks).label('average_score')
        ).filter(Attempt.StudentID == student_id).scalar()
        if average_score is None:
            average_score = 0

        # Fetch attempts over time
        attempts_over_time = db.session.query(
            Attempt.Marks,
            Attempt.TotalMarks
        ).filter(Attempt.StudentID == student_id).order_by(Attempt.AttemptDate).all()

        # Highest Score
        highest_score_attempt = db.session.query(Attempt).filter(
            Attempt.StudentID == student_id
        ).order_by(db.desc(Attempt.Marks)).first()
        highest_score = highest_score_attempt.Marks if highest_score_attempt else 0

        return jsonify({
            'total_attempts': [{'subject': row.subject_name, 'count': row.total_attempts} for row in total_attempts],
            'average_scores': [{'subject': row.subject_name, 'average_score': row.average_score} for row in average_scores],
            'average_score': average_score,
            'total_exams': total_exams or 0,
            'attempts_over_time': [{'score': row.Marks, 'total_marks': row.TotalMarks} for row in attempts_over_time],
            'highest_score': highest_score
        }), 200

    except Exception as e:
        return jsonify({'message': 'Error fetching dashboard data', 'error': str(e)}), 500
    
#@authentication('student')
@student_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if Student.query.filter_by(Email=data.get('email')).first():
        return jsonify({'message': 'An account with this email already exists'}), 409
    try:
        student = Student(
            Name=data.get('name'),
            Email=data.get('email').lower(),
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

@authentication('student')
@student_bp.route('/<int:student_id>', methods=['GET'])
def get_student(student_id):
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'message': 'Student not found'}), 404
        return jsonify({
            'student_id': student.StudentID,
            'name': student.Name,
            'email': student.Email,
            'dob': student.DOB.strftime('%Y-%m-%d'),
            'college_name': student.CollegeName,
            'degree': student.Degree
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching student ID', 'error': str(e)}), 500

@authentication('student')
@student_bp.route('/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json()
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'message': 'Student not found'}), 404
        student.Name = data.get('name', student.Name)
        student.Email = data.get('email', student.Email)
        student.DOB = datetime.strptime(data.get('dob', student.DOB.strftime('%Y-%m-%d')), '%Y-%m-%d')
        student.CollegeName = data.get('college_name', student.CollegeName)
        student.Degree = data.get('degree', student.Degree)
        db.session.commit()
        return jsonify({'message': 'Student updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating student', 'error': str(e)}), 500

@authentication('student')
@student_bp.route('/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'message': 'Student not found'}), 404
        db.session.delete(student)
        db.session.commit()
        return jsonify({'message': 'Student deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting student', 'error': str(e)}), 500

@authentication('student')
@student_bp.route('/subjects', methods=['GET'])
def get_subjects():
    try:
        subjects = Subject.query.all()
        return jsonify([{
            'subject_id': subject.SubjectID,
            'subject_name': subject.SubjectName,
        } for subject in subjects]), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching subjects', 'error': str(e)}), 500

@authentication('student')
@student_bp.route('/chapters', methods=['GET'])
def get_chapters():
    try:
        subject_id = request.args.get('subject_id', type=int)
        if subject_id:
            chapters = Chapter.query.filter_by(SubjectID=subject_id).all()
            if not chapters:
                return jsonify({'message': 'No chapters found for this subject'}), 404
            return jsonify([{
                'chapter_id': chapter.ChapterID,
                'chapter_name': chapter.ChapterName,
                'subject_id': chapter.SubjectID
            } for chapter in chapters]), 200
        else:
            chapters = Chapter.query.all()
            return jsonify([{
                'chapter_id': chapter.ChapterID,
                'chapter_name': chapter.ChapterName,
                'subject_id': chapter.SubjectID
            } for chapter in chapters]), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching chapters', 'error': str(e)}), 500

@authentication('student')
@student_bp.route('/exams', methods=['GET'])
def get_exams():
    try:
        chapter_id = request.args.get('chapter_id', type=int)
        subject_id = request.args.get('subject_id', type=int)

        query = Exam.query.filter_by(Published=True)

        if subject_id:
            exams = query.join(Chapter).filter(Chapter.SubjectID == subject_id).all()
        elif chapter_id:
            exams = query.filter_by(ChapterID=chapter_id).all()
        else:
            exams = query.all()

        if not exams:
            return jsonify([]), 200
            
        return jsonify([{
            'exam_id': exam.ExamID,
            'exam_name': exam.ExamName,
            'total_marks': exam.TotalMarks,
            'total_questions': exam.TotalQuestions,
            'total_duration': exam.TotalDuration,
            'exam_date': exam.ExamDate.strftime('%Y-%m-%d %H:%M:%S'),
            'chapter_id': exam.ChapterID,
            'exam_type': exam.ExamType,
            'start_time': exam.StartTime.strftime('%Y-%m-%d %H:%M:%S') if exam.StartTime else None
        } for exam in exams]), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching exams', 'error': str(e)}), 500

#== Exam Attempts ==
@authentication('student')
@student_bp.route('/<int:student_id>/exam/<int:exam_id>/start', methods=['POST'])
def start_exam(student_id, exam_id):
    try:
        exam = Exam.query.options(joinedload(Exam.questions)).get(exam_id)

        if not exam:
            return jsonify({'message': 'Exam not found'}), 404
        
        new_attempt = Attempt(
            StudentID=student_id,
            ExamID=exam_id,
            AttemptDate=datetime.utcnow(),
            Marks=0,
            TotalMarks=exam.TotalMarks
        )
        db.session.add(new_attempt)
        db.session.commit()

        questions_data = [{
            'QuestionID': q.QuestionID,
            'QuestionStatement': q.QuestionStatement,
            'Option1': q.Option1,
            'Option2': q.Option2,
            'Option3': q.Option3,
            'Option4': q.Option4,
            'Marks': q.Marks,
            'NegMarks': q.NegMarks
        } for q in exam.questions]

        return jsonify({
            'message': 'Exam started successfully',
            'attempt_id': new_attempt.AttemptID,
            'exam_details': {
                'exam_name': exam.ExamName,
                'total_duration': exam.TotalDuration,
                'total_questions': exam.TotalQuestions,
            },
            'questions': questions_data
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error starting exam', 'error': str(e)}), 500

@student_bp.route('/<int:student_id>/attempt/<int:attempt_id>/submit', methods=['POST'])
def submit_exam(student_id, attempt_id):
    try:
        data = request.get_json()
        answers = data.get('answers')
        #print("\n--- SUBMIT EXAM INITIATED ---")
        #print(f"Attempt ID: {attempt_id}, Student ID: {student_id}")
        #print(f"Received answers payload: {answers}")

        attempt = Attempt.query.filter_by(AttemptID=attempt_id, StudentID=student_id).first()
        if not attempt:
            return jsonify({'message': 'Attempt not found or unauthorized'}), 404

        exam = Exam.query.options(joinedload(Exam.questions)).get(attempt.ExamID)

        total_score = 0
        question_map = {q.QuestionID: q for q in exam.questions}
        #print(f"Processing {len(answers)} answers for attempt ID: {attempt_id}")

        for question_id_str, selected_option_str in answers.items():
            question_id = int(question_id_str)
            
            if selected_option_str is None:
                #print(f"\n  Skipping Question ID: {question_id} (not answered)")
                continue
                
            selected_option = int(selected_option_str)
            question = question_map.get(question_id)

            #print(f"\n  Processing Question ID: {question_id}")
            #print(f"  Student's Answer: {selected_option}, Correct Answer: {question.CorrectOption}")

            if question:
                correct = (question.CorrectOption == selected_option)
                negative_marks = question.NegMarks or 0

                if correct:
                    total_score += question.Marks
                    #print(f"  Result: CORRECT. Awarding {question.Marks} marks.")
                else:
                    total_score -= abs(negative_marks)
                    #print(f"  Result: INCORRECT. Deducting {abs(negative_marks)} marks.")

                #print(f"  Current Running Score: {total_score}")
                # Store the student's answer
                selected_answer = SelectedAnswer(
                    AttemptID=attempt_id,
                    QuestionID=question_id,
                    SelectedOption=selected_option
                )
                db.session.add(selected_answer)

        attempt.Marks = total_score
        #print(f"\nFinal Calculated Score: {total_score}")
        #print("Updating attempt record in the database...")
        db.session.commit()
        #print("--- SUBMIT EXAM COMPLETED ---\n")

        return jsonify({
            'message': 'Exam submitted successfully!',
            'attempt_id': attempt_id,
            'score': total_score,
            'total_marks': exam.TotalMarks
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error submitting exam', 'error': str(e)}), 500

@authentication('student')
@student_bp.route('/<int:student_id>/attempt/<int:attempt_id>/results', methods=['GET'])
def get_exam_results(student_id, attempt_id):
    try:
        attempt = db.session.query(Attempt).filter(Attempt.AttemptID == attempt_id, Attempt.StudentID == student_id).options(
            joinedload(Attempt.exam).joinedload(Exam.questions),
            joinedload(Attempt.SelectedAnswers)
        ).first()

        if not attempt:
            return jsonify({'message': 'Attempt not found or unauthorized'}), 404

        answers_map = {sa.QuestionID: sa.SelectedOption for sa in attempt.SelectedAnswers}

        results_data = []
        for question in attempt.exam.questions:
            results_data.append({
                'QuestionStatement': question.QuestionStatement,
                'Option1': question.Option1,
                'Option2': question.Option2,
                'Option3': question.Option3,
                'Option4': question.Option4,
                'CorrectOption': question.CorrectOption,
                'YourAnswer': answers_map.get(question.QuestionID, -1),
                'Marks': question.Marks,
                'NegMarks': question.NegMarks
            })

        return jsonify({
            'attempt_id': attempt.AttemptID,
            'exam_name': attempt.exam.ExamName,
            'score': attempt.Marks,
            'total_marks': attempt.TotalMarks,
            'results': results_data
        }), 200

    except Exception as e:
        return jsonify({'message': 'Error fetching results', 'error': str(e)}), 500

@authentication('student')
@student_bp.route('/<int:student_id>/history', methods=['GET'])
def get_history(student_id):
    try:
        attempts = Attempt.query.options(joinedload(Attempt.exam))\
                                .filter_by(StudentID=student_id)\
                                .order_by(desc(Attempt.AttemptDate)).all()
        history_data = []
        for attempt in attempts:
            history_data.append({
                'attempt_id': attempt.AttemptID,
                'exam_id': attempt.ExamID,
                'exam_name': attempt.exam.ExamName,
                'marks_obtained': attempt.Marks,
                'total_marks': attempt.TotalMarks,
                'attempt_date': attempt.AttemptDate.strftime('%Y-%m-%d %H:%M:%S')
            })

        return jsonify(history_data), 200

    except Exception as e:
        return jsonify({'message': 'Error fetching attempt history', 'error': str(e)}), 500
    
@authentication('student')
@student_bp.route('/<int:student_id>/history/export', methods=['POST'])
def export_history(student_id):
    try:
        
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'message': 'Student not found'}), 404
        
        from app.celery_tasks import export_student_history_to_csv    
        export_student_history_to_csv.delay(student.StudentID)

        return jsonify({'message': 'Your quiz history is being exported and will be sent to your email.'}), 202
    
    except Exception as e:
        return jsonify({'message': 'Error triggering export', 'error': str(e)}), 500

