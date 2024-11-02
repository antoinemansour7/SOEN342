from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# Association table for many-to-many relationship between User and Offering
attendees = db.Table('attendees',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('offering_id', db.Integer, db.ForeignKey('offering.id'), primary_key=True)
)

# New Location model
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    offerings = db.relationship('Offering', backref='location', lazy=True)

    def __repr__(self):
        return f"Location('{self.name}', '{self.city}', '{self.address}')"


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
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    maximum_capacity = db.Column(db.Integer, nullable=False)
    available_spots = db.Column(db.Integer, nullable=False, default=0)
    attendees = db.relationship('User', secondary=attendees, backref=db.backref('attended_offerings', lazy='dynamic'))

    def __init__(self, lesson_type, location_id, start_time, end_time, maximum_capacity):
        self.lesson_type = lesson_type
        self.location_id = location_id
        self.start_time = start_time
        self.end_time = end_time
        self.maximum_capacity = maximum_capacity
        self.available_spots = maximum_capacity

    def __repr__(self):
        return f"Offering('{self.lesson_type}', 'Location ID: {self.location_id}', '{self.start_time}', '{self.end_time}')"
