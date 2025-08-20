from extensions import db

class Questions(db.Model):
    __tablename__ = 'Questions'  

    Question_ID = db.Column(db.Integer, primary_key=True)
    Quiz_ID = db.Column(db.Integer, db.ForeignKey('Quizzes.Quiz_ID', ondelete="CASCADE"), nullable=False)
    Question_Statement = db.Column(db.Text, nullable=False)

    Option1 = db.Column(db.String(255), nullable=False)
    Option2 = db.Column(db.String(255), nullable=False)
    Option3 = db.Column(db.String(255), nullable=False)
    Option4 = db.Column(db.String(255), nullable=False)
    Correct_Option = db.Column(db.Integer, nullable=False)

    # Relationship with Quizzes (Ensure proper back_populates)
    quiz = db.relationship('Quizzes', back_populates='questions')
    responses = db.relationship('Response', back_populates='question', lazy=True)



    def __repr__(self):
        return f"<Question {self.Question_ID}: {self.Question_Statement[:30]}...>"