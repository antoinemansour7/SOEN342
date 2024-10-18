from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin



db = SQLAlchemy()


attendees = db.Table('attendees',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('offering_id', db.Integer, db.ForeignKey('offering.id'))
)

# User model: Admin, Instructor, Customer
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String(50), nullable=False, default='client')  # 'admin', 'instructor', 'client'

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"


class Offering(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    maximum_capacity = db.Column(db.Integer, nullable=False)
    available_spots = db.Column(db.Integer, nullable=False, default=0)
    attendees = db.relationship('User', secondary=attendees, backref='attended_offerings')

    def __init__(self, lesson_type, location, start_time, end_time, maximum_capacity):
        self.lesson_type = lesson_type
        self.location = location
        self.start_time = start_time
        self.end_time = end_time
        self.maximum_capacity = maximum_capacity
        self.available_spots = maximum_capacity


attendees = db.Table('attendees',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('offering_id', db.Integer, db.ForeignKey('offering.id'), primary_key=True),
    extend_existing=True  # Add this line to prevent the table redefinition error
)

