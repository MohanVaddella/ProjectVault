from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, g
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_mail import Mail
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from flask_jwt_extended.exceptions import NoAuthorizationError, JWTDecodeError, JWTExtendedException
from werkzeug.security import check_password_hash

from extensions import db, bcrypt, jwt, mail
from datetime import timedelta
import pyotp
from dotenv import load_dotenv
import os


from models import User
from auth import auth_bp
from vault import vault_bp

load_dotenv()

app = Flask(__name__)


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')


app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true') == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))

app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

mail.init_app(app)
db.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)



app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(vault_bp, url_prefix='/vault')

@app.before_request
def load_current_user():
    
    public_routes = ['home', 'auth.register', 'auth.login']
    print(f"Checking JWT for request: {request.cookies}")
    if request.endpoint in public_routes or request.path.startswith('/static'):
        g.current_user = None
    else:
        try:
            
            verify_jwt_in_request()
            token = get_jwt_identity()
            if token:
                g.current_user = User.query.get(token) 
                print(f"User loaded: {g.current_user}") 
            else:
                g.current_user = None
        except ExpiredSignatureError:
            flash("Session expired. Please login again.", "warning")
            g.current_user = None
            return redirect(url_for('auth.login'))
        except InvalidTokenError:
            flash("Invalid token. Please login again.", "danger")
            g.current_user = None
            return redirect(url_for('auth.login'))
        except NoAuthorizationError:
            g.current_user = None
        except JWTDecodeError as e:
            print(f"JWT Decode Error: {e}")
            g.current_user = None


@app.context_processor
def inject_current_user():
    return {'current_user': g.current_user or None}


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
@jwt_required()  
def dashboard():
    return render_template('dashboard.html')

@app.route('/vault')
@jwt_required()  
def vault():
    return render_template('vault.html')


@app.errorhandler(401)
def unauthorized(e):
    flash("Please login to access this page.", "danger")
    return redirect(url_for('auth.login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
