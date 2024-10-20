from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Regexp, Length
from flask_wtf.file import FileAllowed


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(),
    Regexp(r'^\d+$', message="Phone number must contain only digits"),
    Length(min=10, max=10, message="Phone number must be 10 digits")])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message="Email is required"), Email(message="Invalid email")])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class DocumentForm(FlaskForm):
    document_type = SelectField('Document Type', choices=[
        ('PAN', 'PAN Card'),
        ('AADHAAR', 'Aadhaar Card'),
        ('PASSPORT', 'Passport'),
        ('PHOTO', 'Photo')
    ], validators=[DataRequired()])
    
    document = FileField('Upload Document', validators=[
        FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF or Image files only!'),
        DataRequired()
    ])
    
    submit = SubmitField('Upload')
