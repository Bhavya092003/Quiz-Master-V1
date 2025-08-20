from extensions import db
from datetime import datetime
from models.questions_model import Questions


class Response(db.Model):
    __tablename__ = 'responses'

    Response_ID = db.Column(db.Integer, primary_key=True)
    User_ID = db.Column(db.Integer, db.ForeignKey('Users.User_ID'), nullable=False)
    Quiz_ID = db.Column(db.Integer, db.ForeignKey('Quizzes.Quiz_ID'), nullable=False)
    Question_ID = db.Column(db.Integer, db.ForeignKey('Questions.Question_ID'), nullable=False)
    selected_option = db.Column(db.String(255), nullable=False)

    # Relationships
    user = db.relationship('Users', back_populates='responses')  # Updated back_populates name
    quiz = db.relationship('Quizzes', back_populates='responses')  # Use string reference
    question = db.relationship('Questions', back_populates='responses')




    def __repr__(self):
        return f'<Response {self.Response_ID}>'


