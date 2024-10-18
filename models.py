from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

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
    lesson_type = db.Column(db.String(100), nullable=False)  # e.g., 'swimming', 'yoga'
    mode = db.Column(db.String(50), nullable=False)  # 'group', 'private'
    location = db.Column(db.String(150), nullable=False)
    start_time = db.Column(db.String(50), nullable=False)
    end_time = db.Column(db.String(50), nullable=False)
    schedule = db.Column(db.String(100), nullable=False)  # e.g., 'Sundays 12PM-3PM'
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_available = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"Offering('{self.lesson_type}', '{self.mode}', '{self.location}', '{self.schedule}')"

