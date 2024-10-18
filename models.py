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
    mode = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    maximum_capacity = db.Column(db.Integer, nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    attendees = db.relationship('User', secondary='attendees', backref='offerings')



    def __repr__(self):
        return f"Offering('{self.lesson_type}', '{self.mode}', '{self.location}', '{self.schedule}')"

