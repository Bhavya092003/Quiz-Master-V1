from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from extensions import db

class Scores(db.Model):
    Score_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    User_ID = db.Column(db.Integer, db.ForeignKey('Users.User_ID'))
    User_Name = db.Column(db.String(100))
    Quiz_ID = db.Column(db.Integer, db.ForeignKey('Quizzes.Quiz_ID'))
    Quiz_Name = db.Column(db.String(255))
    Subject_Name = db.Column(db.String(255))
    Chapter_Name = db.Column(db.String(255))
    Score = db.Column(db.Integer)
    Number_of_Questions = db.Column(db.Integer)
    Attempt_Date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # Attempt_Time = db.Column(db.Time, default=datetime.utcnow().time, nullable=False)
    Attempt_Time = db.Column(db.Time, default=lambda: datetime.utcnow().time(), nullable=False)
 

    def __init__(self, User_ID, User_Name, Quiz_ID, Quiz_Name, Subject_Name, Chapter_Name, Score, Attempt_Date, Attempt_Time, Number_of_Questions):
        self.User_ID = User_ID
        self.User_Name = User_Name
        self.Quiz_ID = Quiz_ID
        self.Quiz_Name = Quiz_Name
        self.Subject_Name = Subject_Name
        self.Chapter_Name = Chapter_Name
        self.Score = Score
        self.Attempt_Date = Attempt_Date
        self.Number_of_Questions = Number_of_Questions
        self.Attempt_Time = Attempt_Time

