from extensions import db  # Import db from extensions
from flask_login import UserMixin

# Updated attendees table to track clients and children
attendees_table = db.Table('attendees',
    db.Column('client_id', db.Integer, db.ForeignKey('client.id'), primary_key=True),
    db.Column('offering_id', db.Integer, db.ForeignKey('offering.id'), primary_key=True)
)


# Catalog classes for each model
class OfferingsCatalog:
    offerings = []

    @classmethod
    def get_all_offerings(cls):
        try:
            return Offering.query.all()  # Fetch directly from the database if in app context
        except RuntimeError:
            return cls.offerings  # Fallback to the in-memory list if outside app context


class InstructorsCatalog:
    instructors = []

    @classmethod
    def get_all_instructors(cls):
        try:
            return Instructor.query.all()
        except RuntimeError:
            return cls.instructors


class LocationsCatalog:
    locations = []

    @classmethod
    def get_all_locations(cls):
        try:
            return Location.query.all()
        except RuntimeError:
            return cls.locations


class BookingsCatalog:
    bookings = []

    @classmethod
    def get_all_bookings(cls):
        try:
            return Booking.query.all()
        except RuntimeError:
            return cls.bookings





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
    role = db.Column(db.String(50), default="client")

    # Relationships
    
    bookings = db.relationship('Booking', back_populates='client', lazy=True)
    children = db.relationship('Child', backref='guardian', lazy=True, cascade="all, delete-orphan")
    offerings = db.relationship('Offering', secondary=attendees_table, back_populates='attendees')


    def __repr__(self):
        return f"Client('{self.username}', '{self.name}')"


# Instructor model
class Instructor(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    specialization = db.Column(db.String(100), nullable=False)  # e.g., "yoga", "swimming"
    password = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default="instructor")

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



class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=True)
    offering_id = db.Column(db.Integer, db.ForeignKey('offering.id'), nullable=False)
    lesson_type = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.String(50), nullable=False)
    end_time = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)

    # Relationships to Client, Child, and Offering
    client = db.relationship('Client', back_populates='bookings')
    child = db.relationship('Child')
    offering = db.relationship('Offering', back_populates='bookings')

    def __init__(self, offering_id, lesson_type, start_time, end_time, date, client_id=None, child_id=None):
        self.client_id = client_id
        self.child_id = child_id
        self.offering_id = offering_id
        self.lesson_type = lesson_type
        self.start_time = start_time
        self.end_time = end_time
        self.date = date

    def __repr__(self):
        return f"Booking(Lesson Type: {self.lesson_type}, Date: {self.date}, Time: {self.start_time} - {self.end_time})"



class Offering(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_type = db.Column(db.String(50), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    maximum_capacity = db.Column(db.Integer, nullable=True)
    available_spots = db.Column(db.Integer, nullable=False, default=0)
    offering_type = db.Column(db.String(20), nullable=False, default="General")
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'), nullable=True)
    is_assigned = db.Column(db.Boolean, default=False)  # Track if offering is assigned
    attendees = db.relationship('Client', secondary=attendees_table, back_populates='offerings')
  

    # Relationships
    bookings = db.relationship('Booking', back_populates='offering', cascade="all, delete-orphan")

    def __init__(self, lesson_type, location_id, start_time, end_time, maximum_capacity, offering_type="General"):
        self.lesson_type = lesson_type
        self.location_id = location_id
        self.start_time = start_time
        self.end_time = end_time
        self.maximum_capacity = maximum_capacity
        self.available_spots = maximum_capacity
        self.offering_type = offering_type



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




class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    organisation = db.Column(db.String(100), nullable=False, default="Unified Learning Solutions")
    username = db.Column(db.String(150), nullable=False, unique=True, default="admin")
    password = db.Column(db.String(150), nullable=False, default="adminaccount")
    role = db.Column(db.String(50), default="admin")

    def __init__(self, username="admin", password="adminaccount", organisation="Unified Learning Solutions"):
        self.username = username
        self.password = password
        self.organisation = organisation

    def __repr__(self):
        return f"Admin(Organisation: {self.organisation})"






