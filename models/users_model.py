from extensions import db
from datetime import date
from dateutil import parser  # For robust date parsing
from models.subject_model import Subjects  # Make sure the model is imported
from werkzeug.security import generate_password_hash, check_password_hash

class Users(db.Model):
    __tablename__ = 'Users'
    
    User_ID = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(100), nullable=False, unique=True)  # Email as username
    Password = db.Column(db.String(200), nullable=False)  # Store hashed password
    Full_name = db.Column(db.String(100), nullable=False)
    Qualification = db.Column(db.String(100), nullable=True)
    DOB = db.Column(db.Date, nullable=False)

    responses = db.relationship('Response', back_populates='user')  # Updated back_populates name
    # quiz_attempts = db.relationship('QuizAttempts', back_populates='user')  # Updated back_populates name


    def set_password(self, password):
        self.Password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.Password, password)


