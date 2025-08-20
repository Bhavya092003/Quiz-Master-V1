from flask import render_template, request, redirect, url_for, session
from models.users_model import Users
from extensions import db
from datetime import datetime

def login():
    if request.method == 'POST':
        email = request.form['Email']
        password = request.form['Password']
        user = Users.query.filter_by(Email=email).first() 
        if user and user.check_password(password):
            session['user_id'] = user.User_ID
            session['user_name'] = user.Full_name
            session['user_role'] = 'Admin' if user.User_ID == 1 else 'User'
            if session['user_role'] == 'Admin':
                    return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard', user_name=user.Full_name))
        else:
            error = "Invalid email or password"
            return render_template('login.html', error=error)
    return render_template('login.html')

def registration():
    if request.method == 'POST':
        email = request.form['Email']
        full_name = request.form['Full_name']
        qualification = request.form['Qualification']
        dob = request.form['DOB']
        dob = datetime.strptime(dob, '%Y-%m-%d').date()
        password = request.form['Password']
        user = Users(Email=email, Full_name=full_name, Qualification=qualification, DOB=dob)
        user.set_password(password) #hashkiya
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login_route'))

    return render_template('registration.html')

def logout():
    session.clear() #session khali
    return redirect(url_for('login_route'))
