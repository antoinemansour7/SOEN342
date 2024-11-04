from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, BooleanField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange, Optional
from models import Location


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

    def validate_username(self, username):
        from models import Instructor  # Delayed import to avoid circular dependency
        instructor = Instructor.query.filter_by(username=username.data).first()
        if instructor:
            raise ValidationError('That username is already taken. Please choose a different one.')

class ClientRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone = StringField('Phone', validators=[Optional(), Length(min=10, max=15)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=1, max=120, message="Age must be between 1 and 120.")])

    add_child = BooleanField('Add Child')
    # Make child fields optional but validate conditionally in custom methods
    child_name = StringField('Child Name', validators=[Optional()])
    child_age = IntegerField('Child Age', validators=[Optional(), NumberRange(min=0, max=17, message="Child age must be between 0 and 17.")])
    child_relation = StringField('Relation to Child', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Register as Client')

    def validate_username(self, username):
        from models import Client  # Delayed import
        client = Client.query.filter_by(username=username.data).first()
        if client:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_age(self, age):
        if age.data < 18:
            raise ValidationError('Clients must be at least 18 years old. Please register the individual as a child instead.')

    # Conditional validation for child fields based on 'add_child' checkbox
    def validate_child_name(self, child_name):
        if self.add_child.data and not child_name.data:
            raise ValidationError('Child name is required if adding a child.')

    def validate_child_age(self, child_age):
        if self.add_child.data and not child_age.data:
            raise ValidationError('Child age is required if adding a child.')

    def validate_child_relation(self, child_relation):
        if self.add_child.data and not child_relation.data:
            raise ValidationError('Child relation is required if adding a child.')





class OfferingForm(FlaskForm):
    lesson_type = StringField('Lesson Type', validators=[DataRequired(), Length(min=2, max=50)])
    offering_type = SelectField('Offering Type', choices=[('Group', 'Group'), ('Private', 'Private')], validators=[DataRequired()])
    location = SelectField('Location', coerce=int, validators=[DataRequired()])
    start_time = DateTimeField('Start Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_time = DateTimeField('End Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    maximum_capacity = IntegerField('Maximum Capacity', validators=[Optional()])
    submit = SubmitField('Create Offering')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate location choices from the database
        self.location.choices = [(location.id, f"{location.name} - {location.city}") for location in Location.query.all()]

    def validate_maximum_capacity(self, maximum_capacity):
        # Ensure maximum_capacity is provided if offering_type is 'Group'
        if self.offering_type.data == 'Group' and not maximum_capacity.data:
            raise ValidationError('Please provide a maximum capacity for group offerings.')




class LocationForm(FlaskForm):
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=100)])
    address = StringField('Address', validators=[DataRequired(), Length(min=5, max=255)])
    name = StringField('Location Name', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Create Location')