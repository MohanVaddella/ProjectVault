from extensions import db  
from datetime import datetime
from sqlalchemy import Enum

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    kyc_documents = db.relationship('KYC', backref='owner', lazy=True, cascade="all, delete-orphan")

class KYC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(db.String(50), nullable=False)  
    file_path = db.Column(db.String(256), nullable=False)  
    status = db.Column(db.Enum('pending', 'approved', 'rejected', name='kyc_status'), default='pending', nullable=False)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class AccessToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(256), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
