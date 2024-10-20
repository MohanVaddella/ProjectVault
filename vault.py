import os
import hashlib
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import KYC
from extensions import db
from utils import encrypt_file, decrypt_file, allowed_file, generate_access_token

vault_bp = Blueprint('vault', __name__)

@vault_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_kyc_document():
    user_id = get_jwt_identity()
    file = request.files.get('file')
    document_type = request.form.get('document_type')

    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    file.save(file_path)
    encrypted_file_path = encrypt_file(file_path, user_id)
    file_hash = hashlib.sha256(open(encrypted_file_path, 'rb').read()).hexdigest()

    new_doc = KYCDocument(user_id=user_id, document_type=document_type, filename=filename, file_hash=file_hash)
    db.session.add(new_doc)
    db.session.commit()

    return jsonify({'message': 'Document uploaded successfully', 'file_hash': file_hash}), 201

@vault_bp.route('/documents', methods=['GET'])
@jwt_required()
def list_kyc_documents():
    user_id = get_jwt_identity()
    documents = KYCDocument.query.filter_by(user_id=user_id).all()
    doc_list = [{'filename': doc.filename, 'status': doc.status, 'file_hash': doc.file_hash} for doc in documents]
    return jsonify({'documents': doc_list}), 200

@vault_bp.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download_kyc_document(filename):
    user_id = get_jwt_identity()
    document = KYCDocument.query.filter_by(user_id=user_id, filename=filename).first()

    if not document:
        return jsonify({'error': 'Document not found'}), 404

    encrypted_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(encrypted_file_path):
        return jsonify({'error': 'File not found'}), 404

    decrypted_file_path = decrypt_file(encrypted_file_path, user_id)
    return send_from_directory(directory=current_app.config['UPLOAD_FOLDER'], filename=decrypted_file_path)

@vault_bp.route('/delete/<filename>', methods=['DELETE'])
@jwt_required()
def delete_kyc_document(filename):
    user_id = get_jwt_identity()
    document = KYCDocument.query.filter_by(user_id=user_id, filename=filename).first()

    if not document:
        return jsonify({'error': 'Document not found'}), 404

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(document)
    db.session.commit()

    return jsonify({'message': 'Document deleted successfully'}), 200

@vault_bp.route('/request_access', methods=['POST'])
@jwt_required()
def request_document_access():
    user_id = get_jwt_identity()
    file_hash = request.json.get('file_hash')
    document = KYCDocument.query.filter_by(user_id=user_id, file_hash=file_hash).first()

    if not document:
        return jsonify({'error': 'Document not found or access not granted'}), 404

    access_token = generate_access_token(user_id, file_hash)
    return jsonify({'message': 'Access token generated', 'access_token': access_token}), 200
