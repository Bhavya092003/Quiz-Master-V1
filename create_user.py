from extensions import db
from models.chapter_model import Chapters
from models.users_model import Users

new_user = Users(
    Email='admin@admin.com',
    Password='admin',
    Full_name='admin',
    Qualification='admin',
    DOB='1990-01-01'
)

db.session.add(new_user)
db.session.commit()

print("User created successfully!")
