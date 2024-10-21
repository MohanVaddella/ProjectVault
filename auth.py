from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, make_response
from models import User
from extensions import db, bcrypt, mail
from forms import RegistrationForm, LoginForm
from flask_jwt_extended import create_access_token, set_access_cookies
from datetime import timedelta
import pyotp  
from flask_mail import Message  
import random 



auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'GET':
        
        return render_template('register.html', form=form)
    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        phone = form.phone.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        
        
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first() or User.query.filter_by(phone=phone).first():
            flash("User already exists", "danger")
            return jsonify({"message": "User already exists"}), 400

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(name=name, email=email, phone=phone, password_hash=password_hash)

        db.session.add(new_user)
        db.session.commit()

        flash("User registered successfully", "success")
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html', form=form)
    
    if form.validate_on_submit():  
        email = form.email.data
        password = form.password.data


        
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash("User does not exist", "danger")
            return redirect(url_for('auth.login'))
        

        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            
            otp = random.randint(100000, 999999)  
            
            msg = Message("Your OTP Code", recipients=[email])
            msg.body = f"Your OTP code is {otp}. Please enter it to securely manage your KYC documents and provide consent-based access to banks and agencies."
            mail.send(msg)

            
            session['otp'] = otp  
            session['user_id'] = user.id  

            return render_template('verify_otp.html')  

        flash("Invalid email or password", "danger")
        return redirect(url_for('auth.login'))  

    return render_template('login.html', form=form)

@auth_bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    otp_entered = str(request.form.get('otp'))
    expected_otp = str(session.get('otp'))
    user_id = session.get('user_id')

    if expected_otp and otp_entered == expected_otp:
        user = User.query.get(user_id)
        if user is None:
            flash("User not found", "danger")
            return redirect(url_for('auth.login'))
        token = create_access_token(identity=user_id, expires_delta=timedelta(hours=1))
        

        
        print(f"Token generated: {token}")
        
        
        
        response = make_response(redirect(url_for('vault.view_dashboard')))
        set_access_cookies(response, token)
        
        
        return response 

    else:
        print(f"OTP mismatch: {otp_entered} != {expected_otp}")
        flash("Invalid OTP", "danger")
        return redirect(url_for('auth.login'))
