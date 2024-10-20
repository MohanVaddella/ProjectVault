from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from dotenv import load_dotenv
import os


db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
migrate = Migrate()

def create_app():
    
    load_dotenv()

    
    app = Flask(__name__)

    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')  
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')

    
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    
    from .auth import auth_bp
    from .vault import vault

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(vault, url_prefix='/vault')
    
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    
    with app.app_context():
        from . import app  

    return app
