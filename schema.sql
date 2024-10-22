CREATE DATABASE IF NOT EXISTS vault;
USE vault;


CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX (name),
    INDEX (email),
    INDEX (phone)
);


CREATE TABLE IF NOT EXISTS kyc (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_type VARCHAR(50) NOT NULL,
    filename VARCHAR(256) NOT NULL,
    file_path VARCHAR(256) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    status ENUM('not_used', 'pending', 'approved', 'denied') DEFAULT 'not_used' NOT NULL,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS kyc_request (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    access_token VARCHAR(512) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    bank_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS access_token (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token VARCHAR(512) NOT NULL,
    user_id INT NOT NULL,
    expires_at DATETIME NOT NULL,
    file_hash VARCHAR(64),
    INDEX (token),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

