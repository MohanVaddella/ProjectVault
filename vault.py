import os
import hashlib
from flask import Blueprint, request, jsonify, current_app, send_from_directory, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask_mail import Message
from werkzeug.utils import secure_filename
from models import User, KYC, KYCRequest, AccessToken
from extensions import db, mail
from utils import encrypt_file, decrypt_file, allowed_file, generate_access_token
from forms import KYCForm
from datetime import datetime, timedelta

vault_bp = Blueprint('vault', __name__)

@vault_bp.route('/upload', methods=['GET'])
@jwt_required()
def view_vault():
    user_id = get_jwt_identity()
    documents = KYC.query.filter_by(user_id=user_id).all()
    
    if not documents:  
        flash('No KYC documents found for this user.', 'info')
        
    return render_template('vault.html', documents=documents, form=KYCForm())

@vault_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def view_dashboard():
    user_id = get_jwt_identity()
    documents = KYC.query.filter_by(user_id=user_id).all()
    total_documents = len(documents)
    
    kyc_requests = KYCRequest.query.filter_by(user_id=user_id).all()
    
    approved_documents = [req for req in kyc_requests if req.status == 'approved']
    pending_requests = KYCRequest.query.filter_by(user_id=user_id, status='pending').all()
    
    if not documents:  
        flash('No KYC documents found for this user.', 'info')
        
    return render_template(
        'dashboard.html',
        documents=documents,
        total_documents=total_documents,
        approved_documents=approved_documents,
        pending_requests=pending_requests
    )

@vault_bp.route('/upload', methods=['POST', 'GET'])
@jwt_required()
def upload_kyc_document():
    form = KYCForm()
    user_id = get_jwt_identity()

    
    if request.method == 'GET':
        return render_template('vault.html', form=form)

    
    if form.validate_on_submit():
        file = form.document.data
        document_type = form.document_type.data

        if not file or not allowed_file(file.filename):
            flash('Invalid file type', 'danger')
            return redirect(url_for('vault.view_vault'))

        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        
        file.save(file_path)
        encrypted_file_path = encrypt_file(file_path, user_id)
        file_hash = hashlib.sha256(open(encrypted_file_path, 'rb').read()).hexdigest()

        
        new_doc = KYC(user_id=user_id, document_type=document_type, filename=filename, file_path=encrypted_file_path, file_hash=file_hash, status='not_used')
        db.session.add(new_doc)
        db.session.commit()

        flash('Document uploaded successfully', 'success')
        return redirect(url_for('vault.view_vault'))

    return render_template('vault.html', form=form)

@vault_bp.route('/delete/<int:doc_id>', methods=['POST'])
@jwt_required()
def delete_kyc_document(doc_id):
    user_id = get_jwt_identity()
    document = KYC.query.filter_by(user_id=user_id, id=doc_id).first()

    if not document:
        flash('Document not found', 'danger')
        return redirect(url_for('vault.view_vault'))

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(document)
    db.session.commit()

    flash('Document deleted successfully', 'success')
    return redirect(url_for('vault.view_vault'))

@vault_bp.route('/update/<int:doc_id>', methods=['POST', 'GET'])
@jwt_required()
def update_kyc_document(doc_id):
    user_id = get_jwt_identity()
    document = KYC.query.filter_by(user_id=user_id, id=doc_id).first()
    
    if not document:
        flash('Document not found', 'danger')
        return redirect(url_for('vault.view_vault'))

    if request.method == 'POST':
        
        new_document_type = request.form.get('document_type')
        file = request.files['document']

        if not file or not allowed_file(file.filename):
            flash('Invalid file type', 'danger')
            return redirect(url_for('vault.update_kyc_document', doc_id=doc_id))

        
        old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document.filename)
        if os.path.exists(old_file_path):
            os.remove(old_file_path)

        
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        
        encrypted_file_path = encrypt_file(file_path, user_id)
        file_hash = hashlib.sha256(open(encrypted_file_path, 'rb').read()).hexdigest()

        
        document.document_type = new_document_type
        document.filename = filename
        document.file_path = encrypted_file_path
        document.file_hash = file_hash

        db.session.commit()

        flash('Document updated successfully', 'success')
        return redirect(url_for('vault.view_vault'))

    return render_template('update_kyc.html', document=document)

@vault_bp.route('/request_kyc_access', methods=['GET', 'POST'])
def request_kyc_access():
    if request.method == 'GET':
        
        users = User.query.all()  
        print(users)
    
        return render_template('bank_interface.html', users=users)
    if request.method == 'POST':
        user_id = request.form.get('user_id')  
        document_type = request.form.get('document_type')
        bank_name = request.form.get('bank_name')
        
        print("user_id:", user_id)
        
        existing_request = KYCRequest.query.filter_by(user_id=user_id, document_type=document_type, bank_name=bank_name, status='pending').first()
        if existing_request:
            flash("A KYC access request is already pending for this user and document type.", "warning")
            return redirect(url_for('vault.request_kyc_access'))


        
        new_request = KYCRequest(user_id=user_id, document_type=document_type, bank_name=bank_name, status="pending", access_token="NULL")
        db.session.add(new_request)
        
        kyc_doc = KYC.query.filter_by(user_id=user_id, document_type=document_type).first()
        if kyc_doc:
            kyc_doc.status = 'pending'
            
        db.session.commit()
        
        user = User.query.get(user_id)  

    if user:
        
        login_link = url_for('auth.login', _external=True)
        
        
        msg = Message(
            subject="KYC Verification Request",
            recipients=[user.email],
            html=render_template(
                'kyc_request_email.html',
                user_name=user.name,
                bank_name=bank_name,
                document_type=document_type,
                login_link=login_link
            )
        )
        
        
        try:
            mail.send(msg)
            flash('KYC request created and email notification sent to the user.', 'success')
        except Exception as e:
            flash('Failed to send email notification.', 'danger')
            print(f"Error sending email: {e}")

        return redirect(url_for('vault.request_kyc_access'))


@vault_bp.route('/approve_kyc_request/<int:request_id>', methods=['POST'])
@jwt_required()
def approve_kyc_request(request_id):
    user_id = get_jwt_identity()
    kyc_request = KYCRequest.query.filter_by(id=request_id, user_id=user_id).first()

    if not kyc_request:
        flash('Request not found', 'danger')
        return redirect(url_for('vault.view_dashboard'))
    
    kyc_doc = KYC.query.filter_by(user_id=kyc_request.user_id, document_type=kyc_request.document_type).first()
    if not kyc_doc:
        flash('KYC document not found', 'danger')
        return redirect(url_for('vault.view_dashboard'))

    file_hash = kyc_doc.file_hash
    
    new_token = create_access_token(identity=user_id)
    print(len(new_token))
    expiry_time = datetime.utcnow() + timedelta(days=30)

    kyc_request.access_token = new_token
    kyc_request.status = 'approved'
    
    kyc_doc.status = 'approved'
    
    access_token_entry = AccessToken(token=new_token, user_id=kyc_request.user_id, expires_at=expiry_time, file_hash=file_hash)
    db.session.add(access_token_entry)
    
    db.session.commit()
    

    flash('KYC request approved', 'success')
    return redirect(url_for('vault.view_dashboard'))


@vault_bp.route('/deny_kyc_request/<int:request_id>', methods=['POST'])
@jwt_required()
def deny_kyc_request(request_id):
    user_id = get_jwt_identity()
    kyc_request = KYCRequest.query.filter_by(id=request_id, user_id=user_id).first()

    if not kyc_request:
        flash('Request not found', 'danger')
        return redirect(url_for('vault.view_dashboard'))

    kyc_request.status = 'denied'
    
    kyc_doc = KYC.query.filter_by(user_id=kyc_request.user_id, document_type=kyc_request.document_type).first()
    if kyc_doc:
        kyc_doc.status = 'denied'
        
    db.session.commit()

    flash('KYC request denied', 'danger')
    return redirect(url_for('vault.view_dashboard'))

