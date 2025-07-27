from app.extension import celery, mail
from flask_mail import Message
from app.models import Student, Exam, Attempt
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
import io
import csv

@celery.task
def send_new_exam_notification(exam_id):
    """
    Sends an email to all students when a new exam is published.
    """
    exam = Exam.query.get(exam_id)
    if not exam:
        return "Exam not found."

    students = Student.query.all()
    if not students:
        return "No students to notify."

    subject = f"New Quiz Published: {exam.ExamName}"
    body = f"""
    Hi students,

    A new quiz, '{exam.ExamName}', has just been published.

    It covers the topic: {exam.chapter.ChapterName}
    Total Marks: {exam.TotalMarks}
    Duration: {exam.TotalDuration} minutes

    Log in to your dashboard to attempt it. Good luck!

    Thanks,
    The QuizMaster Team
    """

    # Use a connection to send emails in a batch, which is more efficient
    with mail.connect() as conn:
        for student in students:
            msg = Message(subject=subject, recipients=[student.Email], body=body)
            conn.send(msg)
            
    return f"Notification sent for exam '{exam.ExamName}' to {len(students)} students."


@celery.task
def send_daily_reminders():
    """
    Sends a daily email to students with exams that are due today.
    """
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
    try:
        student = Student.query.get(student_id)
        if not student:
            return "Student not found."
        print(student)
        #fetch all attempts filter by student id all time
        attempts = Attempt.query.filter_by(StudentID=student_id)
        print(attempts)
        if not attempts:
            report_body = f"""
            <p>Hi {student.Name},</p>
            <p>You have not attempted any quizzes in the last 30 days.</p>
            <p>Thanks,<br>The QuizMaster Team</p>
            """
        else:
            table_rows = ""
            for attempt in attempts:
                table_rows += f"""
                <tr>
                    <td>{attempt.AttemptDate.strftime('%Y-%m-%d %H:%M')}</td>
                    <td>{attempt.exam.ExamName}</td>
                    <td>{attempt.TotalMarks}</td>
                    <td>{attempt.Marks}</td>
                </tr>
                """

            report_body = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: sans-serif; }}
                        table {{ border-collapse: collapse; width: 100%; }}
                        th, td {{ border: 1px solid #dddddd; text-align: left; padding: 8px; }}
                        th {{ background-color: #f2f2f2; }}
                    </style>
                </head>
                <body>
                    <h2>Hi {student.Name},</h2>
                    <p>Here is your monthly performance report:</p>
                    <table>
                        <thead>
                            <tr>
                                <th>Attempt Date</th>
                                <th>Exam Name</th>
                                <th>Total Marks</th>
                                <th>Marks Obtained</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows}
                        </tbody>
                    </table>
                    <p>Keep up the great work!</p>
                    <p>Thanks,<br>The QuizMaster Team</p>
                </body>
            </html>
            """

        msg = Message(
            "Your Monthly Performance Report",
            recipients=[student.Email],
            html=report_body
        )
        mail.send(msg)
        return f"Monthly report sent to {student.Name}."
    except Exception as e:
        print(f"Error generating monthly report: {e}")
        return "Error generating monthly report."

@celery.task
def generate_exam_report_for_student(student_id):
    """
    Generates a performance report for a specific exam for a student and sends it via email.
    """
    student = Student.query.get(student_id)
    if not student:
        return "Student not found."

    last_month = datetime.utcnow() - timedelta(days=30)
    attempts = Attempt.query.options(joinedload(Attempt.exam)).filter(
        Attempt.StudentID == student_id,
        Attempt.AttemptDate >= last_month
    ).order_by(Attempt.AttemptDate.desc()).all()

    if not attempts:
        report_body = f"""
        <p>Hi {student.Name},</p>
        <p>You have not attempted any quizzes in the last 30 days.</p>
        <p>Keep up the great work!</p>
        <p>Thanks,<br>The QuizMaster Team</p>
        """
        csv_data = None
    else:
        table_rows = ""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Attempt Date', 'Exam Name', 'Total Marks', 'Marks Obtained'])
        for attempt in attempts:
            table_rows += f"""
            <tr>
                <td>{attempt.AttemptDate.strftime('%Y-%m-%d %H:%M')}</td>
                <td>{attempt.exam.ExamName}</td>
                <td>{attempt.TotalMarks}</td>
                <td>{attempt.Marks}</td>
            </tr>
            """
            writer.writerow([
                attempt.AttemptDate.strftime('%Y-%m-%d %H:%M'),
                attempt.exam.ExamName,
                attempt.TotalMarks,
                attempt.Marks
            ])
        csv_data = output.getvalue()
        report_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: sans-serif; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #dddddd; text-align: left; padding: 8px; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <h2>Hi {student.Name},</h2>
                <p>Here is your performance report for the last 30 days:</p>
                <table>
                    <thead>
                        <tr>
                            <th>Attempt Date</th>
                            <th>Exam Name</th>
                            <th>Total Marks</th>
                            <th>Marks Obtained</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
                <p>Keep up the great work!</p>  
                <p>Thanks,<br>The QuizMaster Team</p>
            </body>
        </html>
        """

    msg = Message(
        "Your Monthly Performance Report",
        recipients=[student.Email],
        html=report_body
    )

    if csv_data:
        msg.attach(
            "performance_report.csv",
            "text/csv",
            csv_data
        )

    mail.send(msg)
    #print(f"Exam report for the last 30 days sent to {student.Name}.")
    return f"Exam report for the last 30 days sent to {student.Name}."

@celery.task
def export_student_history_to_csv(student_id):
    student = Student.query.get(student_id)
    if not student:
        return "Student not found"

    attempts = Attempt.query.filter_by(StudentID=student_id).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Attempt ID', 'Exam Name', 'Marks Obtained', 'Total Marks', 'Attempt Date'])
    
    for attempt in attempts:
        writer.writerow([
            attempt.AttemptID,
            attempt.exam.ExamName,
            attempt.Marks,
            attempt.TotalMarks,
            attempt.AttemptDate.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    csv_data = output.getvalue()
    
    msg = Message(
        "Your Quiz History Export",
        recipients=[student.Email],
        body="Please find your quiz history attached."
    )
    
    # Correctly attach the file
    msg.attach(
        "quiz_history.csv",
        "text/csv",
        csv_data
    )
    
    mail.send(msg)
    return f"Quiz history sent to {student.Email}"

@celery.task
def export_all_student_reports():
    """
    Triggers the generation of an exam performance report for every student.
    """
    students = Student.query.all()
    for student in students:
        generate_exam_report_for_student.delay(student.StudentID)
    return f"Triggered performance report generation for {len(students)} students."