import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey') 
    DEBUG = False 

    
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///site.db')  
    SQLALCHEMY_TRACK_MODIFICATIONS = False  

    
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwtsecretkey')  
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)) 

    
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads') 
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  

class DevelopmentConfig(Config):
    
    DEBUG = True  
    SQLALCHEMY_ECHO = True  

class ProductionConfig(Config):
    
    DEBUG = False  
    SQLALCHEMY_ECHO = False  
    SESSION_COOKIE_SECURE = True  

class TestingConfig(Config):
    
    TESTING = True  
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'  
    WTF_CSRF_ENABLED = False  
    JWT_ACCESS_TOKEN_EXPIRES = 1  


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
