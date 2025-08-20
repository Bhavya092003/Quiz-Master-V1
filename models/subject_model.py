from extensions import db

class Subjects(db.Model):
    __tablename__ = 'Subjects'
    Subject_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Subject_name = db.Column(db.String(255), nullable=False)
    Students_ID = db.Column(db.Integer, db.ForeignKey('Users.User_ID'))  # Foreign key linking to Users table



    chapters = db.relationship('Chapters', back_populates='subject', lazy=True)

    quizzes = db.relationship('Quizzes', back_populates='subject')

    def __repr__(self):
        return f'Subject with name {self.Subject_name} and id {self.Subject_ID}'
