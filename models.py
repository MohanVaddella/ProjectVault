from extensions import db  
from datetime import datetime
from sqlalchemy import Enum

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    kyc_documents = db.relationship('KYC', backref='owner', lazy=True, cascade="all, delete-orphan")

class KYC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(db.String(50), nullable=False) 
    filename = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(256), nullable=False)
    file_hash = db.Column(db.String(64), nullable=False)  
    status = db.Column(db.Enum('not_used', 'pending', 'approved', 'denied', name='kyc_status'), default='not_used', nullable=False)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
class KYCRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)
    access_token = db.Column(db.String(512), nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bank_name = db.Column(db.String(255), nullable=False)
    user = db.relationship('User', backref='kyc_requests', lazy=True)


class AccessToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(512), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    file_hash = db.Column(db.String(64), nullable=True)
