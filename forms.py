from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, BooleanField  # Updated imports if necessary
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange
from models import *  # Updated import

# Login Form Definition
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class InstructorRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    specialization = StringField('Specialization', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone = StringField('Phone', validators=[Length(min=10, max=15)])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Register as Instructor')

    # Validator to check if username already exists for Instructor
    def validate_username(self, username):
        instructor = Instructor.query.filter_by(username=username.data).first()
        if instructor:
            raise ValidationError('That username is already taken. Please choose a different one.')

# Client Registration Form with optional Child Information
class ClientRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone = StringField('Phone', validators=[Length(min=10, max=15)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=1, max=120, message="Age must be between 1 and 120.")])

    # Optional child information fields
    add_child = BooleanField('Add Child')
    child_name = StringField('Child Name')
    child_age = IntegerField('Child Age', validators=[NumberRange(min=0, max=17, message="Child age must be between 0 and 17.")])
    child_relation = StringField('Relation to Child', validators=[Length(max=50)])

    submit = SubmitField('Register as Client')

    # Validator to check if username already exists for Client
    def validate_username(self, username):
        client = Client.query.filter_by(username=username.data).first()
        if client:
            raise ValidationError('That username is already taken. Please choose a different one.')

    # Validator for age
    def validate_age(self, age):
        if age.data < 18:
            raise ValidationError('Clients must be at least 18 years old. Please register the individual as a child instead.')

    # Optional validation for child fields if the checkbox is selected
    def validate_child_name(self, child_name):
        if self.add_child.data and not child_name.data:
            raise ValidationError('Child name is required if adding a child.')

    def validate_child_age(self, child_age):
        if self.add_child.data and not child_age.data:
            raise ValidationError('Child age is required if adding a child.')

    def validate_child_relation(self, child_relation):
        if self.add_child.data and not child_relation.data:
            raise ValidationError('Child relation is required if adding a child.')