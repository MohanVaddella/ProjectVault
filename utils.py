import os
import hashlib
from cryptography.fernet import Fernet

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encrypt_file(file_path, user_id):
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    with open(file_path, 'rb') as f:
        file_data = f.read()
    encrypted_data = cipher_suite.encrypt(file_data)

    encrypted_file_path = file_path + '.enc'
    with open(encrypted_file_path, 'wb') as f:
        f.write(encrypted_data)
    os.remove(file_path)
    return encrypted_file_path

def decrypt_file(encrypted_file_path, user_id):
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    with open(encrypted_file_path, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = cipher_suite.decrypt(encrypted_data)

    decrypted_file_path = encrypted_file_path.replace('.enc', '')
    with open(decrypted_file_path, 'wb') as f:
        f.write(decrypted_data)
    return decrypted_file_path

def generate_access_token(user_id, file_hash):
    from flask_jwt_extended import create_access_token
    token = create_access_token(identity={'user_id': user_id, 'file_hash': file_hash})
    return token
