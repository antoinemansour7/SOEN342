from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# Catalog classes for each model
class OfferingsCatalog:
    offerings = []

    @classmethod
    def get_all_offerings(cls):
        return cls.offerings


class InstructorsCatalog:
    instructors = []

    @classmethod
    def get_all_instructors(cls):
        return cls.instructors


class LocationsCatalog:
    locations = []

    @classmethod
    def get_all_locations(cls):
        return cls.locations


class BookingsCatalog:
    bookings = []

    @classmethod
    def get_all_bookings(cls):
        return cls.bookings


# New Booking association class for Client and Offering
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    offering_id = db.Column(db.Integer, db.ForeignKey('offering.id'), nullable=False)
    lesson_type = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.String(50), nullable=False)
    end_time = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)

    # Relationships to Client and Offering
    client = db.relationship('Client', back_populates='bookings')
    offering = db.relationship('Offering', back_populates='bookings')

    def __init__(self, client_id, offering_id, lesson_type, start_time, end_time, date):
        self.client_id = client_id
        self.offering_id = offering_id
        self.lesson_type = lesson_type
        self.start_time = start_time
        self.end_time = end_time
        self.date = date
        
        # Automatically add to BookingsCatalog
        BookingsCatalog.bookings.append(self)

    def __repr__(self):
        return f"Booking(Lesson Type: {self.lesson_type}, Date: {self.date}, Time: {self.start_time} - {self.end_time})"


# New Child model for clients who register with children
class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    age = db.Column(db.String(10), nullable=False)
    relation = db.Column(db.String(50), nullable=False)  # e.g., "son", "daughter"
    guardian_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)

    def __repr__(self):
        return f"Child('{self.name}', Age: {self.age}, Relation: {self.relation})"


# Client model: Represents a regular customer
class Client(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    password = db.Column(db.String(150), nullable=False)
    age = db.Column(db.String(10), nullable=False)

    # Relationships
    children = db.relationship('Child', backref='guardian', lazy=True)
    bookings = db.relationship('Booking', back_populates='client', lazy=True)

    def __repr__(self):
        return f"Client('{self.username}', '{self.name}')"


# Instructor model
class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    specialization = db.Column(db.String(100), nullable=False)  # e.g., "yoga", "swimming"
    password = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    city = db.Column(db.String(100), nullable=False)

    # Relationship with Offering
    offerings = db.relationship('Offering', backref='instructor', lazy=True)

    def __init__(self, username, specialization, password, phone, city):
        self.username = username
        self.specialization = specialization
        self.password = password
        self.phone = phone
        self.city = city

        # Automatically add to InstructorsCatalog
        InstructorsCatalog.instructors.append(self)

    def __repr__(self):
        return f"Instructor('{self.username}', Specialization: {self.specialization}, City: {self.city})"


class Offering(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_type = db.Column(db.String(50), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    maximum_capacity = db.Column(db.Integer, nullable=False)
    available_spots = db.Column(db.Integer, nullable=False, default=0)
    
    # Foreign key linking Offering to Instructor
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'), nullable=False)

    # Relationship with Booking
    bookings = db.relationship('Booking', back_populates='offering', lazy=True)

    def __init__(self, lesson_type, location_id, start_time, end_time, maximum_capacity, instructor_id):
        self.lesson_type = lesson_type
        self.location_id = location_id
        self.start_time = start_time
        self.end_time = end_time
        self.maximum_capacity = maximum_capacity
        self.available_spots = maximum_capacity
        self.instructor_id = instructor_id
        
        # Automatically add the new offering to OfferingsCatalog
        OfferingsCatalog.offerings.append(self)

    def __repr__(self):
        return f"Offering('{self.lesson_type}', 'Location ID: {self.location_id}', Instructor ID: {self.instructor_id}, '{self.start_time}', '{self.end_time}')"


# Location model
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    offerings = db.relationship('Offering', backref='location', lazy=True)

    def __init__(self, city, address, name):
        self.city = city
        self.address = address
        self.name = name
        
        # Automatically add to LocationsCatalog
        LocationsCatalog.locations.append(self)

    def __repr__(self):
        return f"Location('{self.name}', '{self.city}', '{self.address}')"
