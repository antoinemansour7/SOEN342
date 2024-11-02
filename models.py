from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# Association table for many-to-many relationship between Client and Offering
attendees = db.Table('attendees',
    db.Column('client_id', db.Integer, db.ForeignKey('client.id'), primary_key=True),
    db.Column('offering_id', db.Integer, db.ForeignKey('offering.id'), primary_key=True)
)

# New Child model for clients who register with children
class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    age = db.Column(db.String(10), nullable=False)
    relation = db.Column(db.String(50), nullable=False)  # e.g., "son", "daughter"
    guardian_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)

    def __repr__(self):
        return f"Child('{self.name}', Age: {self.age}, Relation: {self.relation})"

# Client model: Admin, Instructor, Customer
class Client(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    password = db.Column(db.String(150), nullable=False)
    age = db.Column(db.String(10), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='client')  # 'admin', 'instructor', 'client'
    
    # Guardian-child relationship
    children = db.relationship('Child', backref='guardian', lazy=True)

    def __repr__(self):
        return f"Client('{self.username}', '{self.name}', '{self.role}')"

class Offering(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_type = db.Column(db.String(50), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    maximum_capacity = db.Column(db.Integer, nullable=False)
    available_spots = db.Column(db.Integer, nullable=False, default=0)
    attendees = db.relationship('Client', secondary=attendees, backref=db.backref('attended_offerings', lazy='dynamic'))

    def __init__(self, lesson_type, location_id, start_time, end_time, maximum_capacity):
        self.lesson_type = lesson_type
        self.location_id = location_id
        self.start_time = start_time
        self.end_time = end_time
        self.maximum_capacity = maximum_capacity
        self.available_spots = maximum_capacity

    def __repr__(self):
        return f"Offering('{self.lesson_type}', 'Location ID: {self.location_id}', '{self.start_time}', '{self.end_time}')"

# New Location model
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    offerings = db.relationship('Offering', backref='location', lazy=True)

    def __repr__(self):
        return f"Location('{self.name}', '{self.city}', '{self.address}')"
