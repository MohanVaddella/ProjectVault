# ProjectVault

  Securely manage your KYC documents and provide consent-based access to banks and agencies.

## Table of Contents

- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Running the Application](#running-the-application)

## Technologies Used

- **Frontend**: HTML, CSS, Bootstrap
- **Backend**: Flask, Python
- **Database**: MySQL
- **Other Libraries**: Flask-JWT-Extended, Flask-SQLAlchemy, Flask-Migrate, Flask-WTF, Flask-Bcrypt, python-dotenv

## Project Structure

```bash
projectvault/
├── __init__.py
├── .env
├── .gitignore
├── app.py
├── auth.py
├── config.py
├── extensions.py
├── forms.py
├── models.py
├── requirements.txt
├── schema.sql
├── utils.py
├── vault.py
├── templates/
│   ├── 404.html
│   ├── bank_interface.html
│   ├── base.html
│   ├── dashboard.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── update_kyc.html
│   ├── vault.html
│   └── verify_otp.html
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── images/
│   │   └── logo.jpeg
│   └── js/
└── uploads/
```

## Setup Instructions

### 1. Clone the Repository:

  ```bash
  git clone https://github.com/MohanVaddella/ProjectVault.git
  cd ProjectVault
  ```
### 2. Install Dependencies:

  You can install the necessary Python packages listed in requirements.txt by running:

  ```bash
  pip install -r requirements.txt
  ```

  Dependencies include:

  - Flask
  - Flask-JWT-Extended
  - Flask-SQLAlchemy
  - Flask-Migrate
  - Flask-WTF
  - Flask-Bcrypt
  - python-dotenv

### 3. Create a .env file:

  In the root directory, create a .env file and add the following environment variables:

  ```bash
  SECRET_KEY=<your-secret-key>
  DATABASE_URI=mysql+pymysql://root:<your-db-password>@localhost/vault
  JWT_SECRET_KEY=<your-jwt-secret-key>
  UPLOAD_FOLDER=uploads
  JWT_ACCESS_TOKEN_EXPIRES=3600
  MAIL_SERVER=smtp.gmail.com
  MAIL_PORT=587
  MAIL_USE_TLS=true
  MAIL_USERNAME=<your-email>
  MAIL_PASSWORD=<your-app-password>
  MAIL_DEFAULT_SENDER=<your-email>
  ```

## Running the Application

### 1. Run the Flask App:
  To start the Flask application, use the following command:

  ```bash
  export FLASK_APP=app.py
  flask run
  ```

  Visit http://127.0.0.1:5000/ in your browser to view the application.

### 2. Access the Admin Panel:

To access the *KYC vault* dashboard, login with the registered credentials and start using the application.


  
