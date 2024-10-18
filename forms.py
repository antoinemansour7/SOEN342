from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField  # Ensure all necessary imports are here
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange
from models import User

# Login Form Definition
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=1, max=120)])
    role = SelectField('Role', choices=[('customer', 'Customer'), ('instructor', 'Instructor')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    # Validator to check if username already exists
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    # Validator to check if email already exists
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one.')
        




class OfferingForm(FlaskForm):
    lesson_type = StringField('Lesson Type', validators=[DataRequired()])
    mode = SelectField('Mode', choices=[('group', 'Group'), ('private', 'Private')], validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    start_time = StringField('Start Time', validators=[DataRequired()])
    end_time = StringField('End Time', validators=[DataRequired()])
    schedule = StringField('Schedule', validators=[DataRequired()])
    submit = SubmitField('Create Offering')

