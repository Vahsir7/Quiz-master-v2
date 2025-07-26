from .extension import celery, mail
from flask_mail import Message
from .models import Student, Exam, Attempt
from datetime import datetime, timedelta

@celery.task
def send_daily_reminders():
    today = datetime.utcnow().date()
    upcoming_exams = Exam.query.filter(Exam.ExamDate.date() == today, Exam.Published == True).all()
    if not upcoming_exams:
        return "No upcoming exams today."
    students = Student.query.all()
    for student in students:
        attempted_exam_ids = {a.ExamID for a in student.attempts}
        pending_exams = [exam for exam in upcoming_exams if exam.ExamID not in attempted_exam_ids]

        if pending_exams:
            exam_names = ", ".join([exam.ExamName for exam in pending_exams])
            msg = Message(
                "Quiz Reminder!",
                recipients=[student.Email],
                body=f"Hi {student.Name},\n\nThis is a reminder that the following quizzes are due today: {exam_names}.\n\nGood luck!\nQuizMaster Team"
            )
            mail.send(msg)
    return f"Sent reminders for {len(upcoming_exams)} exams."

@celery.task
def generate_monthly_report(student_id):
    student = Student.query.get(student_id)
    if not student:
        return "Student not found."
    last_month = datetime.utcnow() - timedelta(days=30)
    attempts = Attempt.query.filter(Attempt.StudentID == student_id, Attempt.AttemptDate >= last_month).all()
    if not attempts:
        report_body = "You have not attempted any quizzes in the last 30 days."
    else:
        total_attempts = len(attempts)
        avg_score = sum(a.Marks for a in attempts) / total_attempts if total_attempts > 0 else 0
        report_body = f"""
        Hi {student.Name},

        Here is your monthly performance report:

        - Total Quizzes Taken: {total_attempts}
        - Average Score: {avg_score:.2f}%

        Keep up the great work!

        Thanks,
        The QuizMaster Team
        """

    msg = Message(
        "Your Monthly Performance Report",
        recipients=[student.Email],
        body=report_body
    )
    mail.send(msg)
    return f"Monthly report sent to {student.Email}."