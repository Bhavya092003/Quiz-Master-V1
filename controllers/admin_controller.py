from flask import Flask, redirect, render_template, url_for, request, jsonify, session
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func
from models.subject_model import Subjects
from models.chapter_model import Chapters
from models.quiz_model import Quizzes
from models.questions_model import Questions
from models.scores_model import Scores
from extensions import db
import pdb

def render_admin_template(template):
    return render_template(template, user_role='Admin')

def adminDashboard(app,db):
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login_route"))

    subjects = Subjects.query.all()
    subject_data = []

    for subject in subjects:
        chapters = Chapters.query.filter_by(Subject_ID=subject.Subject_ID).all()
        chapter_list = []

        for chapter in chapters:
            quiz_count = Quizzes.query.filter_by(Chapter_ID=chapter.Chapter_ID).count()
            chapter_list.append({
                'Chapter_ID': chapter.Chapter_ID,
                'Chapter_Name': chapter.Chapter_Name,
                'Quiz_Count': quiz_count
            })
        subject_data.append({
            'Subject_ID': subject.Subject_ID,
            'Subject_Name': subject.Subject_name,
            'Chapters': chapter_list
        })
    return render_template('admin/admin_dashboard.html', subjects=subject_data, user_role='Admin')

def newSubject(app,db):
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login_route"))
    # pdb.set_trace()
    if request.method == 'GET':
        subject = Subjects.query.all()
        return render_template('admin/create_subject.html', subject=subject, user_role='Admin')
    elif request.method == 'POST':
        Subject_name = request.form.get('Subject_name')
        # Subject_ID = int(request.form.get('Subject_ID'))
        subject = Subjects(Subject_name=Subject_name)
        try:
            db.session.add(subject)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
        finally:
            db.session.close()
        return redirect(url_for('admin_dashboard'))

def newChapter(app,db):
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login_route"))
    if request.method == 'GET':
        subject_id = request.args.get('subject_id')
        subjects = Subjects.query.all()
        return render_template('admin/create_chapter.html', subjects=subjects, selected_subject_id=subject_id, user_role='Admin')

    elif request.method == 'POST':
        chapter_name = request.form.get('chapter_name')
        subject_id = request.form.get('subject_id')

        if not chapter_name or not subject_id:
            return "Missing chapter name or subject ID", 400  

        new_chapter = Chapters(Chapter_Name=chapter_name, Subject_ID=subject_id)

        try:
            db.session.add(new_chapter)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            return "Error adding chapter", 500
        return redirect(url_for('admin_dashboard'))

def newQuiz(app, db):
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login_route"))
    if request.method == 'GET':
        subjects = Subjects.query.all()
        # print(subjects)
        return render_template('admin/create_quiz.html', subjects=subjects, user_role='Admin')

    if request.method == 'POST':
        try:
            quiz_name = request.form['quiz_name']
            subject_id = request.form['subject_id']
            chapter_id = request.form.get('chapter_id')
            time_limit = request.form['duration']
            date = request.form['date']

            if not chapter_id:
                return redirect(url_for('quiz_dashboard'))

            chapter_id = int(chapter_id)

            new_quiz = Quizzes(
                Quiz_Name=quiz_name,
                Subject_ID=subject_id,
                Chapter_ID=chapter_id,
                Quiz_Time=time_limit,
                Quiz_Date=date
            )

            db.session.add(new_quiz)
            db.session.commit()
            return redirect(url_for('quiz_dashboard'))

        except Exception as e:
            print(f"Error: {e}")
            return redirect(url_for('quiz_dashboard'))

def deleteQuiz(quiz_id):
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login_route"))
    quiz = Quizzes.query.get(quiz_id)
    if quiz:
        db.session.delete(quiz)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Quiz not found"}), 404

def getChapters(subject_id):
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login_route"))
    try:
        # chapters = Chapter.query.filter_by(Subject_ID=subject_id).all()
        chapters = Chapters.query.filter_by(Subject_ID=subject_id).all()
        
        if not chapters:
            return jsonify([])

        chapter_list = [{"id": c.Chapter_ID, "name": c.Chapter_Name} for c in chapters]
        return jsonify(chapter_list)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def add_question(quiz_id):
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login_route"))
    quiz = Quizzes.query.filter_by(Quiz_ID=quiz_id).first()

    if not quiz:
        return "Quiz not found", 404

    chapter = Chapters.query.filter_by(Chapter_ID=quiz.Chapter_ID).first()
    subject = Subjects.query.filter_by(Subject_ID=quiz.Subject_ID).first()

    if request.method == 'POST':
        statement = request.form.get('statement')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_option = request.form.get('correctOption')
        if not statement or not option1 or not option2 or not option3 or not option4 or not correct_option:
            return "All fields are required!", 400
        correct_option = int(correct_option)

        new_question = Questions(
            Quiz_ID=quiz_id,
            Question_Statement=statement,
            Option1=option1,
            Option2=option2,
            Option3=option3,
            Option4=option4,
            Correct_Option=correct_option
        )
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for('quiz_dashboard'))
    return render_template('admin/create_question.html', quiz=quiz, chapter=chapter, subject=subject)

def viewQuestions(quiz_id):
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login_route"))
    quiz = Quizzes.query.filter_by(Quiz_ID=quiz_id).first()
    if not quiz:
        return "Quiz not found", 404
    questions = Questions.query.filter_by(Quiz_ID=quiz_id).all()
    return render_template('admin/view_questions.html', quiz_name=quiz.Quiz_Name, quiz_id=quiz_id, questions=questions)

def editQuestion(question_id):
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login_route"))
    question = Questions.query.get_or_404(question_id)
    quiz_id = question.Quiz_ID

    if request.method == 'POST':
        try:
            question.Question_Statement = request.form['question_statement']
            question.Option1 = request.form['option1']
            question.Option2 = request.form['option2']
            question.Option3 = request.form['option3']
            question.Option4 = request.form['option4']
            question.Correct_Option = request.form['correct_option']

            db.session.commit()
            return redirect(url_for('view_questions', quiz_id=quiz_id))

        except Exception as e:
            db.session.rollback()
    return render_template('admin/edit_question.html', question=question, quiz_id=quiz_id, user_role='Admin')

def deleteQuestion(question_id):
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login_route"))
    question = Questions.query.get(question_id)
    
    if not question:
        return jsonify({"success": False, "error": "Question not found"}), 404

    try:
        db.session.delete(question)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})

def quizDashboard(app, db):
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login_route"))
    quizzes = (
        db.session.query(Quizzes)
        .join(Chapters, Quizzes.Chapter_ID == Chapters.Chapter_ID)
        .join(Subjects, Chapters.Subject_ID == Subjects.Subject_ID)
        .options(joinedload(Quizzes.questions))
        .all()
    )
    quiz_list = []
    for q in quizzes:
        quiz_data = {
            "Quiz_ID": q.Quiz_ID,
            "Quiz_Name": q.Quiz_Name,
            "Quiz_Date": q.Quiz_Date,
            "Quiz_Time": q.Quiz_Time,
            "Chapter_Name": q.chapter.Chapter_Name,
            "Subject_name": q.chapter.subject.Subject_name,
            "Total_Questions": len(q.questions)
        }
        quiz_list.append(quiz_data)
    return render_template('admin/quiz_dashboard.html', quiz=quiz_list, user_role='Admin')

def editChapter(chapter_id):
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login_route"))
    # pdb.set_trace()
    chapter = Chapters.query.get(chapter_id)

    if not chapter:
        return "Chapter not found", 404
    if request.method == 'POST':
        chapter.Chapter_Name = request.form.get('chapter_name')
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/edit_chapter.html', chapter=chapter)

def deleteChapter(chapter_id):
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login_route"))
    chapter = Chapters.query.get(chapter_id)
    if chapter:
        Quizzes.query.filter_by(Chapter_ID=chapter.Chapter_ID).delete()
        db.session.delete(chapter)
        db.session.commit()
        return '', 204
    return "Chapter not found", 404

def deleteSubject(subject_id):
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login_route"))
    subject = Subjects.query.get(subject_id)
    if subject:
        chapters = Chapters.query.filter_by(Subject_ID=subject_id).all()
        for chapter in chapters:
            Quizzes.query.filter_by(Chapter_ID=chapter.Chapter_ID).delete()
            db.session.delete(chapter)
        db.session.delete(subject)
        db.session.commit()
        return '', 204
    return "Subject not found", 404


def adminSummary(app,db):
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login_route"))
    top_scores_data = (
        db.session.query(Subjects.Subject_name, func.max(Scores.Score))
        .join(Chapters, Subjects.Subject_ID == Chapters.Subject_ID)
        .join(Quizzes, Chapters.Chapter_ID == Quizzes.Chapter_ID)
        .join(Scores, Scores.Quiz_ID == Quizzes.Quiz_ID)
        .group_by(Subjects.Subject_name)
        .all()
    )
    attempt_data = (
        db.session.query(Subjects.Subject_name, func.count(Scores.Quiz_ID))
        .join(Chapters, Subjects.Subject_ID == Chapters.Subject_ID)
        .join(Quizzes, Chapters.Chapter_ID == Quizzes.Chapter_ID)
        .join(Scores, Scores.Quiz_ID == Quizzes.Quiz_ID)
        .group_by(Subjects.Subject_name)
        .all()
    )
    subjects = [row[0] for row in top_scores_data] if top_scores_data else []
    top_scores = [row[1] for row in top_scores_data] if top_scores_data else []
    attempt_subjects = [row[0] for row in attempt_data] if attempt_data else []
    attempts = [row[1] for row in attempt_data] if attempt_data else []
    return render_template(
        "admin/admin_summary.html",
        subjects=subjects,
        top_scores=top_scores,
        attempt_subjects=attempt_subjects,
        attempts=attempts, user_role='Admin'
    )
