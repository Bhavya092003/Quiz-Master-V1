from flask import render_template, session, redirect, url_for, request, jsonify
import json, calendar
from sqlalchemy.sql import func, and_
from extensions import db
from datetime import datetime
from models.quiz_model import Quizzes
from models.subject_model import Subjects
from models.chapter_model import Chapters
from models.users_model import Users
from models.questions_model import Questions
from models.scores_model import Scores
from models.response_model import Response
import pdb

def render_user_template(template):
    return render_template(template, user_role='User')

def userDashboard(user_name):
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login_route"))

    user = Users.query.get(user_id)
    if not user:
        return "User not found", 404
    subjects = Subjects.query.all()
    chapters = Chapters.query.all()

    quizzes = (
        db.session.query(
            Quizzes.Quiz_ID,
            Quizzes.Quiz_Name,
            Quizzes.Quiz_Date,
            Quizzes.Quiz_Time,
            Chapters.Chapter_Name,
            Subjects.Subject_name,
            # func.count(Questions.Question_ID).label("num_questions"),
            func.count(func.distinct(Questions.Question_ID)).label("num_questions"),
            Scores.Attempt_Date,
            Scores.Attempt_Time
        )
        .join(Chapters, Quizzes.Chapter_ID == Chapters.Chapter_ID)
        .join(Subjects, Chapters.Subject_ID == Subjects.Subject_ID)
        .join(Questions, Questions.Quiz_ID == Quizzes.Quiz_ID)
        .outerjoin(Scores, (Scores.Quiz_ID == Quizzes.Quiz_ID) & (Scores.User_ID == user_id))
        .group_by(Quizzes.Quiz_ID)
        .all()
    )
    return render_template("users/user_dashboard.html", quizzes=quizzes, subjects=subjects, chapters=chapters, user_name=user_name)

def view_quiz(user_name,quiz_id):
    quiz = (
        db.session.query(
            Quizzes.Quiz_ID,
            Quizzes.Quiz_Name,
            Quizzes.Quiz_Date,
            Quizzes.Quiz_Time,
            Chapters.Chapter_Name,
            Subjects.Subject_name,
            func.count(Questions.Question_ID).label("num_questions")
        )
        .join(Chapters, Quizzes.Chapter_ID == Chapters.Chapter_ID)
        .join(Subjects, Chapters.Subject_ID == Subjects.Subject_ID)
        .join(Questions, Questions.Quiz_ID == Quizzes.Quiz_ID)
        .filter(Quizzes.Quiz_ID == quiz_id)
        .group_by(Quizzes.Quiz_ID)
        .first()
    )

    if not quiz:
        return "Quiz not found", 404
    return render_template("users/view_quiz.html",user_name=user_name, quiz=quiz)

def start_quiz(user_name,quiz_id):
    quiz = (
        db.session.query(
            Quizzes.Quiz_ID,
            Quizzes.Quiz_Name,
            Quizzes.Quiz_Date,
            Quizzes.Quiz_Time,
            func.count(Questions.Question_ID).label("num_questions")
        )
        .join(Questions, Questions.Quiz_ID == Quizzes.Quiz_ID)
        .filter(Quizzes.Quiz_ID == quiz_id)
        .group_by(Quizzes.Quiz_ID)
        .first()
    )

    if not quiz:
        return "Quiz not found", 404
    try:
        total_minutes = int(quiz.Quiz_Time)  # Quiz_Time is in minutes
        total_seconds = total_minutes * 60
    except (ValueError, TypeError):
        total_seconds = 0

    questions = (
        db.session.query(
            Questions.Question_ID,
            Questions.Question_Statement,
            Questions.Option1,
            Questions.Option2,
            Questions.Option3,
            Questions.Option4
        )
        .filter(Questions.Quiz_ID == quiz_id)
        .all()
    )
    question_list = [
        {
            "Question_ID": q.Question_ID,
            "Question_Statement": q.Question_Statement,
            "Options": [
                {"Option_ID": 1, "Option_Text": q.Option1},
                {"Option_ID": 2, "Option_Text": q.Option2},
                {"Option_ID": 3, "Option_Text": q.Option3},
                {"Option_ID": 4, "Option_Text": q.Option4}
            ]
        } for q in questions
    ]

    user_id = session.get("user_id")
    user = Users.query.get(user_id) if user_id else None

    if not user:
        return redirect(url_for("login_page"))
    return render_template(
        "users/start_quiz.html",
        user=user,
        quiz=quiz,
        user_name=user.Full_name,
        questions=question_list,
        total_seconds=total_seconds
    )

def viewQuiz():
    if request.method=='GET':
        return render_user_template('users/view_quiz.html')

def submit_quiz(user_name, quiz_id):
    try:
        responses = request.json.get("responses")
        user = Users.query.filter_by(Full_name=user_name).first()
        quiz = db.session.query(Quizzes).filter_by(Quiz_ID=quiz_id).first()
        # print(responses)
        # print(user_name)
        if not responses:
            return jsonify({"error": "No responses found"}), 400
        if not user:
            return jsonify({"error": "User not found"}), 404
        if not quiz:
            return {"error": "Quiz not found"}

        user_id = user.User_ID
        quiz_name = quiz.Quiz_Name
        subject_name = quiz.subject.Subject_name
        chapter_name = quiz.chapter.Chapter_Name

        # pdb.set_trace()

        for question_id, answer in responses.items():
            # print(question_id,answer)
            response = Response(
                User_ID=user_id,
                Quiz_ID=quiz_id,
                Question_ID=question_id,
                selected_option=answer
            )
            db.session.add(response)
        db.session.commit()
        quiz_questions = Questions.query.filter_by(Quiz_ID=quiz_id).all()
        score = calculate_score(quiz_id, user_name, responses)
        local_time = datetime.now() 
        user_score = Scores(User_ID=user_id, User_Name=user_name, Quiz_ID=quiz_id, Score=score, Subject_Name=subject_name, Chapter_Name=chapter_name, Quiz_Name=quiz_name, Attempt_Date=local_time.date(), Attempt_Time=local_time.time(),Number_of_Questions=len(quiz_questions))
        db.session.add(user_score)
        db.session.commit()
        return jsonify({"message": "Quiz submitted successfully!", "responses": responses}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error submitting quiz: {e}")
        return jsonify({"error": "An error occurred while submitting the quiz"}), 500   

def calculate_score(quiz_id, user_name, responses):
    score = 0
    correct_answers = get_correct_answers_for_quiz(quiz_id)
    # print(correct_answers)
    for question_id, selected_answer in responses.items():
        correct_answer = correct_answers.get(int(question_id))
        if int(selected_answer) == correct_answer:
            score += 1
    # print(score)
    return score

def get_correct_answers_for_quiz(quiz_id):
    correct_answers = {}
    questions = db.session.query(Questions).filter_by(Quiz_ID=quiz_id).all()
    for question in questions:
        correct_answers[question.Question_ID] = question.Correct_Option
    return correct_answers

def submit_response(user_name, quiz_id):
    user = Users.query.filter_by(Email=user_name).first()    
    if not user:
        return redirect(url_for('error_page', message='User not found'))
    quiz = Quizzes.query.get(quiz_id)
    if not quiz:
        return redirect(url_for('error_page', message='Quiz not found'))
    question_id = request.form.get('question_id')
    selected_option = request.form.get('selected_option')
    question = Questions.query.get(question_id)
    if not question:
        return redirect(url_for('error_page', message='Question not found'))
    response = Response(
        User_ID=user.User_ID,
        Quiz_ID=quiz_id,
        Question_ID=question_id,
        Selected_Option=selected_option
    )
    db.session.add(response)
    db.session.commit()
    return redirect(url_for('user_dashboard', user_name=user_name))

def quiz_results(quiz_id):
    quiz = Quizzes.query.get(quiz_id)
    questions = Questions.query.filter_by(Quiz_ID=quiz_id).all()
    
    if request.method == "POST":
        responses = request.json.get("responses")
        user_name = request.json.get('user_name')
        return render_template(
            "users/quiz_results.html",
            quiz=quiz,
            questions=questions,
            user_name=user_name,
            responses=responses
        )
    return render_template("users/quiz_results.html", quiz=quiz, questions=questions)

def user_scores(user_name):
    user = Users.query.filter_by(Full_name=user_name).first()
    user_id = user.User_ID
    if not user:
        return "User not found", 404
    scores = (
        db.session.query(
            Quizzes.Quiz_Name,
            Scores.Score,
            Scores.Attempt_Date,
            Scores.Attempt_Time,
            func.count(func.distinct(Questions.Question_ID)).label("num_questions")
        )
        .join(Scores, Scores.Quiz_ID == Quizzes.Quiz_ID)
        .join(Questions, Questions.Quiz_ID == Quizzes.Quiz_ID)
        .filter(Scores.User_ID == user_id)
        .group_by(Quizzes.Quiz_ID, Scores.Score, Scores.Attempt_Date)
        .all()
    )

    return render_template('users/scores.html', scores=scores)

def userSummary(user_name):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login_route"))
    subject_attempt_data = (
        db.session.query(Subjects.Subject_name, func.count(Scores.Quiz_ID))
        .join(Chapters, Subjects.Subject_ID == Chapters.Subject_ID)
        .join(Quizzes, Chapters.Chapter_ID == Quizzes.Chapter_ID)
        .join(Scores, (Scores.Quiz_ID == Quizzes.Quiz_ID) & (Scores.User_ID == user_id))
        .group_by(Subjects.Subject_name)
        .all()
    )
    month_attempt_data = (
        db.session.query(func.strftime('%m', Scores.Attempt_Date), func.count(Scores.Quiz_ID))
        .filter(Scores.User_ID == user_id)
        .group_by(func.strftime('%m', Scores.Attempt_Date))
        .all()
    )
    attempted_subjects = [row[0] for row in subject_attempt_data] if subject_attempt_data else []
    attempted_quiz_counts = [row[1] for row in subject_attempt_data] if subject_attempt_data else []
    # months = [row[0] for row in month_attempt_data] if month_attempt_data else []
    months = [calendar.month_name[int(row[0])] for row in month_attempt_data] if month_attempt_data else []
    attempts = [row[1] for row in month_attempt_data] if month_attempt_data else []
    return render_template(
        "users/user_summary.html",
        attempted_subjects=attempted_subjects,
        attempted_quiz_counts=attempted_quiz_counts if attempted_quiz_counts else [],
        quiz_counts=attempted_quiz_counts,
        months=months,
        attempts=attempts,
    )