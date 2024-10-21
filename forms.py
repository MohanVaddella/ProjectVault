from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Regexp, Length
from flask_wtf.file import FileAllowed


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
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

    
class KYCForm(FlaskForm):
    document_type = SelectField('Document Type', choices=[('passport', 'Passport'), ('license', 'Driving License'), ('id', 'National ID')], validators=[DataRequired()])
    document = FileField('Upload Document', validators=[DataRequired(), FileAllowed(['pdf', 'png', 'jpg', 'jpeg'], 'PDF or Image files only!')])
    
    submit = SubmitField('Upload Document')
