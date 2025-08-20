from extensions import db
from datetime import datetime

class Quizzes(db.Model):
    __tablename__ = 'Quizzes'

    Quiz_ID = db.Column(db.Integer, primary_key=True)
    Quiz_Name = db.Column(db.String(255), nullable=False)
    Subject_ID = db.Column(db.Integer, db.ForeignKey('Subjects.Subject_ID', name='fk_quizzes_subject'), nullable=False)
    Chapter_ID = db.Column(db.Integer, db.ForeignKey('Chapters.Chapter_ID', name='fk_quizzes_chapter'), nullable=False)
    Quiz_Date = db.Column(db.String(10), nullable=False)  # Store as TEXT (YYYY-MM-DD)
    Quiz_Time = db.Column(db.String(8), nullable=False)   # Store as TEXT (HH:MM:SS)

    # Relationships
    subject = db.relationship('Subjects', back_populates='quizzes')
    chapter = db.relationship('Chapters', back_populates='quizzes')
    questions = db.relationship('Questions', back_populates='quiz', lazy=True, cascade="all, delete")
    # attempts = db.relationship("QuizAttempts", back_populates="quiz", lazy=True)
    responses = db.relationship('Response', back_populates='quiz')



    def __repr__(self):
        return f"<Quiz ID: {self.Quiz_ID}, Quiz Name: {self.Quiz_Name}, Chapter ID: {self.Chapter_ID}, Date: {self.Quiz_Date}, Time: {self.Quiz_Time}>"

    @staticmethod
    def format_date(date_str):
        """Convert user input (DD/MM/YYYY) to ISO 8601 (YYYY-MM-DD)."""
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")

    @staticmethod
    def format_time(time_str):
        """Convert user input (HH:MM) to ISO 8601 (HH:MM:SS)."""
        return datetime.strptime(time_str, "%H:%M").strftime("%H:%M:%S")
