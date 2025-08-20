from extensions import db

class Chapters(db.Model):
    __tablename__ = 'Chapters'
    Chapter_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Chapter_Name = db.Column(db.String(100), nullable=False)
    Subject_ID = db.Column(db.Integer, db.ForeignKey('Subjects.Subject_ID'), nullable=False)

    # subject = db.relationship('Subjects', backref='subject_relationship', lazy=True)
    quizzes = db.relationship('Quizzes', back_populates='chapter')
    subject = db.relationship('Subjects', back_populates='chapters')

    def __repr__(self):
        return f"<Chapter {self.Chapter_Name}, ID: {self.Chapter_ID}>"
