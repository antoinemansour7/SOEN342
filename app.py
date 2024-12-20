from flask import Flask, render_template, redirect, url_for, flash, request, session
from extensions import db, bcrypt, login_manager  # Import extensions
from flask_migrate import Migrate
from forms import LoginForm, ClientRegistrationForm, InstructorRegistrationForm, OfferingForm, LocationForm
from models import *
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from threading import Lock

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Initialize extensions with the app
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


writer_lock = Lock()
reader_lock = Lock()
reader_count = 0


@login_manager.user_loader
def load_user(user_id):
    user_role = session.get('role')

    if user_role == "admin":
        return Admin.query.get(int(user_id))
    elif user_role == "instructor":
        return Instructor.query.get(int(user_id))
    elif user_role == "client":
        return Client.query.get(int(user_id))
    return None


@app.route('/')
def index():
    assigned_offerings = Offering.query.filter_by(is_assigned=True).all()
    unassigned_offerings = []

    # Show unassigned offerings only for Admin or Instructor
    if current_user.is_authenticated and session.get('role') in ["admin", "instructor"]:
        unassigned_offerings = Offering.query.filter_by(is_assigned=False).all()

    return render_template('index.html', assigned_offerings=assigned_offerings,
                           unassigned_offerings=unassigned_offerings)


# Register choice route
@app.route('/register')
def register():
    return render_template('register_choice.html')  # New template to choose registration type


# Register client route
@app.route('/register_client', methods=['GET', 'POST'])
def register_client():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = ClientRegistrationForm()

    if form.validate_on_submit():
        # Hash the password and create a new Client instance
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        client = Client(
            username=form.username.data,
            name=form.name.data,
            phone=form.phone.data,
            password=hashed_password,
            age=form.age.data
        )

        # Add and commit the client to the database
        db.session.add(client)
        db.session.commit()

        # If the add_child checkbox is selected, process child information
        if form.add_child.data:
            # Only proceed if child fields pass validation and contain data
            if form.child_name.data and form.child_age.data and form.child_relation.data:
                child = Child(
                    name=form.child_name.data,
                    age=form.child_age.data,
                    relation=form.child_relation.data,
                    guardian_id=client.id
                )
                db.session.add(child)
                db.session.commit()

        return redirect(url_for('login'))

    return render_template('register_client.html', form=form)


# Register instructor route
@app.route('/register_instructor', methods=['GET', 'POST'])
def register_instructor():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = InstructorRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        instructor = Instructor(username=form.username.data, specialization=form.specialization.data,
                                password=hashed_password, phone=form.phone.data, city=form.city.data)
        db.session.add(instructor)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('register_instructor.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Assuming LoginForm is your form class
    if form.validate_on_submit():
        user = Admin.query.filter_by(username=form.username.data).first() or \
               Instructor.query.filter_by(username=form.username.data).first() or \
               Client.query.filter_by(username=form.username.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if isinstance(user, Admin):
                session['role'] = 'admin'
            elif isinstance(user, Instructor):
                session['role'] = 'instructor'
            elif isinstance(user, Client):
                session['role'] = 'client'

            login_user(user)
            # Removed success flash message
            return redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/create_offering', methods=['GET', 'POST'])
@login_required
def create_offering():
    if not isinstance(current_user, Admin):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))

    form = OfferingForm()

    if form.validate_on_submit():
        with writer_lock:
            max_capacity = form.maximum_capacity.data if form.offering_type.data == "Group" else 1

            overlap = Offering.query.filter(
                Offering.location_id == form.location.data,
                Offering.start_time < form.end_time.data,
                Offering.end_time > form.start_time.data
            ).first()

            if overlap:
                flash('This location already has an offering scheduled at the same time.', 'danger')
                return render_template('create_offering.html', form=form)

            new_offering = Offering(
                lesson_type=form.lesson_type.data,
                location_id=form.location.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                maximum_capacity=max_capacity,
                offering_type=form.offering_type.data
            )
            new_offering.available_spots = max_capacity

            db.session.add(new_offering)
            db.session.commit()
            OfferingsCatalog.offerings.append(new_offering)

        flash('Offering created successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('create_offering.html', form=form)


def is_location_unique(city, address, name):
    """
    Check if a location with the given city, address, and name already exists.
    """
    existing_location = Location.query.filter_by(city=city, address=address, name=name).first()
    return existing_location is None  # Return True if no existing location is found


@app.route('/create_location', methods=['GET', 'POST'])
@login_required
def create_location():
    # Check if the current user is an admin based on class
    if not current_user.is_authenticated or current_user.__class__.__name__ != 'Admin':
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('index'))

    form = LocationForm()
    if form.validate_on_submit():
        # Check if the location is unique
        if not is_location_unique(form.city.data, form.address.data, form.name.data):
            flash("A location with the same city, address, and name already exists.", "warning")
            return redirect(url_for('create_location'))

        # Create a new location
        location = Location(city=form.city.data, address=form.address.data, name=form.name.data)
        db.session.add(location)
        db.session.commit()

        # Append the new location to the LocationsCatalog
        LocationsCatalog.locations.append(location)

        flash("Location created successfully!", "success")
        return redirect(url_for('index'))

    return render_template('create_location.html', form=form)




@app.route('/logout')
def logout():
    logout_user()

    return redirect(url_for('index'))


@app.route('/unassigned_offerings')
@login_required
def unassigned_offerings():
    if not (isinstance(current_user, Admin) or isinstance(current_user, Instructor)):
        flash('Access restricted to Admins and Instructors.', 'danger')
        return redirect(url_for('index'))

    offerings = Offering.query.filter_by(is_assigned=False).all()
    return render_template('unassigned_offerings.html', offerings=offerings)


@app.route('/claim_offering/<int:offering_id>', methods=['POST'])
@login_required
def claim_offering(offering_id):
    if not isinstance(current_user, Instructor):
        flash('Only instructors can claim offerings.', 'danger')
        return redirect(url_for('index'))

    offering = Offering.query.get_or_404(offering_id)

    # Check if the offering has already been claimed
    if offering.is_assigned:
        flash('This offering has already been claimed.', 'warning')
        return redirect(url_for('unassigned_offerings'))

    # Check if the offering is in the instructor's city and specialty
    if offering.location.city != current_user.city or offering.lesson_type != current_user.specialization:
        flash('You can only claim offerings in your city and specialty.', 'danger')
        return redirect(url_for('unassigned_offerings'))

    # Check if the instructor already has an offering at the same time
    overlapping_offering = Offering.query.filter_by(instructor_id=current_user.id).filter(
        (Offering.start_time < offering.end_time) &
        (Offering.end_time > offering.start_time)
    ).first()
    if overlapping_offering:
        flash('You already have an offering at this time.', 'warning')
        return redirect(url_for('unassigned_offerings'))

    # Assign the offering to the instructor and mark it as assigned
    offering.instructor_id = current_user.id
    offering.is_assigned = True
    db.session.commit()

    flash('Offering successfully claimed!', 'success')
    return redirect(url_for('index'))


@app.route('/attend_offering/<int:offering_id>', methods=['POST'])
@login_required
def attend_offering(offering_id):
    if not isinstance(current_user, Client):
        flash('Only clients can attend offerings.', 'danger')
        return redirect(url_for('index'))

    offering = Offering.query.get_or_404(offering_id)
    child_id = request.form.get('child_id')

    # Conflict check: Restrict to current user and their children
    conflict = Booking.query.filter(
        (
            (Booking.client_id == current_user.id) | 
            (Booking.child_id.in_([child.id for child in current_user.children]))
        ),
        Booking.start_time == offering.start_time,
        Booking.end_time == offering.end_time,
        Booking.date == offering.start_time.date()
    ).first()

    if conflict:
        if conflict.child_id:  # If conflict is for a child
            child = Child.query.get(conflict.child_id)
            conflict_msg = f"Your child {child.name} already has a booking at the same time ({conflict.start_time} - {conflict.end_time})."
        else:
            conflict_msg = f"You already have a booking at the same time ({conflict.start_time} - {conflict.end_time})."
        flash(conflict_msg, 'danger')
        return redirect(request.referrer or url_for('index'))

    # Proceed with booking
    if offering.available_spots > 0:
        if child_id:
            # Booking for child
            child = Child.query.get(child_id)
            if child and child not in offering.attendees:
                offering.attendees.append(current_user)  # Associate client for record
                offering.available_spots -= 1
                booking = Booking(
                    offering_id=offering.id,
                    lesson_type=offering.lesson_type,
                    start_time=offering.start_time,
                    end_time=offering.end_time,
                    date=offering.start_time.date(),
                    client_id=current_user.id,
                    child_id=child.id
                )
                db.session.add(booking)
                db.session.commit()
                flash(f'{child.name} is now attending this offering!', 'success')
            else:
                flash(f'{child.name} is already attending this offering.', 'info')
        else:
            # Booking for the client
            if current_user not in offering.attendees:
                offering.attendees.append(current_user)
                offering.available_spots -= 1
                booking = Booking(
                    offering_id=offering.id,
                    lesson_type=offering.lesson_type,
                    start_time=offering.start_time,
                    end_time=offering.end_time,
                    date=offering.start_time.date(),
                    client_id=current_user.id
                )
                db.session.add(booking)
                db.session.commit()
                flash('You are now attending this offering!', 'success')
    else:
        flash('Sorry, no available spots left for this offering.', 'danger')

    return redirect(url_for('index'))


@app.route('/view_your_bookings')
@login_required
def view_your_bookings():
    if not isinstance(current_user, Client):
        flash('Only clients can view bookings.', 'danger')
        return redirect(url_for('index'))

    # Retrieve bookings associated with the current client
    bookings = Booking.query.filter_by(client_id=current_user.id).all()
    return render_template('view_your_bookings.html', bookings=bookings)


@app.route('/delete_offering/<int:offering_id>', methods=['POST'])
@login_required
def delete_offering(offering_id):
    # Ensure only the admin can delete the offering
    if current_user.role != 'admin':
        flash('Only admins can delete offerings.', 'danger')
        return redirect(url_for('index'))

    offering = Offering.query.get_or_404(offering_id)
    db.session.delete(offering)
    db.session.commit()
    flash('Offering deleted successfully!', 'success')

    # Redirect back to the unassigned offerings page if the user came from there
    if request.referrer and 'unassigned_offerings' in request.referrer:
        return redirect(url_for('unassigned_offerings'))

    return redirect(url_for('index'))


@app.route('/remove_attendee/<int:offering_id>/<int:user_id>', methods=['POST'])
@login_required
def remove_attendee(offering_id, user_id):
    # Ensure only the admin can remove attendees
    if current_user.role != 'admin':
        flash('Only admins can remove attendees.', 'danger')
        return redirect(url_for('view_offering', offering_id=offering_id))

    offering = Offering.query.get_or_404(offering_id)
    attendee = Client.query.get_or_404(user_id)

    # Remove attendee from the offering and increment available spots
    if attendee in offering.attendees:
        offering.attendees.remove(attendee)
        offering.available_spots += 1

        # Remove any associated bookings for this client and offering
        booking = Booking.query.filter_by(client_id=user_id, offering_id=offering_id).first()
        if booking:
            db.session.delete(booking)

        db.session.commit()
        flash('Attendee removed successfully!', 'success')
    else:
        flash('Attendee not found in this offering.', 'info')

    return redirect(url_for('view_offering', offering_id=offering_id))


@app.route('/view_offering/<int:offering_id>')
@login_required  # Optional, if you want only logged-in users to access this
def view_offering(offering_id):
    offering = Offering.query.get_or_404(offering_id)
    return render_template('view_offering.html', offering=offering)


@app.route('/manage_users')
@login_required
def manage_users():
    if not isinstance(current_user, Admin):
        flash('Only admins can access this page.', 'danger')
        return redirect(url_for('index'))

    # Fetch all clients and instructors
    clients = Client.query.all()
    instructors = Instructor.query.all()
    return render_template('manage_users.html', clients=clients, instructors=instructors)


@app.route('/delete_user/<int:user_id>/<user_type>', methods=['POST'])
@login_required
def delete_user(user_id, user_type):
    if not isinstance(current_user, Admin):
        flash('Only admins can delete users.', 'danger')
        return redirect(url_for('index'))

    if user_type == 'client':
        user = Client.query.get_or_404(user_id)

        # Update available spots for each offering the client was attending
        for booking in user.bookings:
            offering = booking.offering
            if offering.available_spots < offering.maximum_capacity:
                offering.available_spots += 1
            db.session.delete(booking)  # Remove the booking record

    elif user_type == 'instructor':
        user = Instructor.query.get_or_404(user_id)

        # Unassign all offerings taught by this instructor
        for offering in user.offerings:
            offering.instructor_id = None  # Unassign instructor
            offering.is_assigned = False

    else:
        flash('Invalid user type specified.', 'danger')
        return redirect(url_for('manage_users'))

    db.session.delete(user)
    db.session.commit()
    flash(f'{user_type.capitalize()} account deleted successfully!', 'success')
    return redirect(url_for('manage_users'))





if __name__ == "__main__":
    app.run(debug=True)
