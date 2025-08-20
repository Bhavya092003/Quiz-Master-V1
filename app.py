from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from controllers.authentication_controller import *
from controllers.admin_controller import *
from controllers.user_controller import *
from extensions import db, migrate
from models.subject_model import Subjects
from models.chapter_model import Chapters
from models.users_model import Users
from models.quiz_model import Quizzes
from models.scores_model import Scores
from models.response_model import Response
import pdb

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.secret_key = 'some key'

db.init_app(app)
migrate.init_app(app, db)

@app.route("/", methods=["GET", "POST"])
def login_route():
    return login()

@app.route('/register', methods=['GET','POST'])
def register():
    return registration()

@app.route('/logout')
def logout_route():
    return logout()

@app.route('/admin-dashboard', methods=['GET','POST'])
def admin_dashboard():
    return adminDashboard(app,db)

@app.route('/admin-dashboard/new_subject', methods=['GET', 'POST'])
def new_subject():
    return newSubject(app,db)

@app.route('/delete_subject/<int:subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    return deleteSubject(subject_id)

@app.route('/admin-dashboard/new_chapter', methods=['GET','POST'])
def new_chapter():
    return newChapter(app,db)

@app.route('/admin-dashboard/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id ):
    # pdb.set_trace()
    return editChapter(chapter_id)

@app.route('/delete_chapter/<int:chapter_id>', methods=['DELETE'])
def delete_chapter(chapter_id):
    return deleteChapter(chapter_id)

@app.route('/admin-dashboard/quiz_dashboard', methods=['GET', 'POST'])
def quiz_dashboard():
    return quizDashboard(app,db)

@app.route('/admin-dashboard/quiz_management/new_quiz', methods=['GET', 'POST'])
def new_quiz():
    # pdb.set_trace()
    return newQuiz(app,db)

@app.route('/admin-dashboard/quiz_management/delete_quiz/<int:quiz_id>', methods=['DELETE'])
def delete_quiz(quiz_id):
    return deleteQuiz(quiz_id)

@app.route('/admin-dashboard/quiz_management/new_quiz/get_chapters/<int:subject_id>', methods=['GET'])
def get_chapters(subject_id):
    return getChapters(subject_id)

@app.route('/admin-dashboard/quiz_management/add_question/<int:quiz_id>', methods=['GET', 'POST'])
def new_question(quiz_id):
    return add_question(quiz_id)

@app.route('/admin-dashboard/quiz_management/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    return editQuestion(question_id)

@app.route('/admin-dashboard/quiz_management/view_questions/<int:quiz_id>')
def view_questions(quiz_id):
    return viewQuestions(quiz_id)

@app.route('/admin-dashboard/quiz_management/delete_question/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    return deleteQuestion(question_id)

@app.route('/admin-dashboard/summary', methods=['GET'])
def admin_summary():
    return adminSummary(app,db)

@app.route('/user-dashboard/<user_name>', methods=['GET','POST'])
def user_dashboard(user_name):
    return userDashboard(user_name)

@app.route('/user-dashboard/<user_name>/view_quiz/<int:quiz_id>', methods=['GET','POST'])
def viewQuiz(user_name,quiz_id):
    return view_quiz(user_name,quiz_id)

@app.route('/user-dashboard/<user_name>/start_quiz/<int:quiz_id>', methods=['GET','POST'])
def startQuiz(user_name,quiz_id):
    quiz = Quizzes.query.get(quiz_id)
    if quiz:
        print(f"Quiz found: {quiz.Quiz_Name}, Quiz_Time: {quiz.Quiz_Time}")
    else:
        print("Quiz not found in DB")
    return start_quiz(user_name,quiz_id)

@app.route('/user-dashboard/<user_name>/submit_quiz/<int:quiz_id>', methods=['POST'])
def submitQuiz(user_name, quiz_id):
    return submit_quiz(user_name,quiz_id)

@app.route('/user-dashboard/<user_name>/submit_quiz/<int:quiz_id>/submit_response', methods=['POST'])
def submitResponse(user_name, quiz_id):
    return submit_response(user_name, quiz_id)


@app.route('/user-dashboard/<user_name>/scores', methods=['GET'])
def userScores(user_name):
    return user_scores(user_name)

@app.route('/user-dashboard/<user_name>/summary', methods=['GET'])
def user_summary(user_name):
    return userSummary(user_name)




@app.route('/quiz-results/<int:quiz_id>', methods=["GET", "POST"])
def quizResults(quiz_id):
    return quiz_results(quiz_id)

if __name__=='__main__':
    app.run(debug=True)