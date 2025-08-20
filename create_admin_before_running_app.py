from app import app, db  # Import your app and db from your main app file
from models.users_model import Users  # Import the Users model
from werkzeug.security import generate_password_hash
from datetime import date

def create_user(email, full_name, password, dob, qualification=None):
    # Check if user already exists
    existing_user = Users.query.filter_by(Email=email).first()
    if existing_user:
        print(f"User with email {email} already exists.")
        return None
    
    # Create a new user instance
    new_user = Users(
        Email=email,
        Full_name=full_name,
        Password=password,
        DOB=dob,
        Qualification=qualification
    )
    
    # Set the hashed password
    new_user.set_password(password)
    
    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    
    print(f"User {full_name} created successfully!")
    return new_user

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure all tables are created if they don't exist
        
        # Example usage to create a new user
        create_user(
            email="Admin@example.com.com",
            full_name="Admin",
            password="admin",
            dob=date(1995, 5, 15),
            qualification="Master's Degree"
        )
