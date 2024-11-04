from flask import Flask, render_template, redirect, url_for, flash, request, session
from extensions import db, bcrypt, login_manager  # Import extensions
from flask_migrate import Migrate
from forms import LoginForm, ClientRegistrationForm, InstructorRegistrationForm, OfferingForm, LocationForm
from models import *
from flask_login import LoginManager, login_user, current_user, logout_user, login_required



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

    return render_template('index.html', assigned_offerings=assigned_offerings, unassigned_offerings=unassigned_offerings)






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
        
        flash('Your client account has been created!', 'success')
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
        instructor = Instructor(username=form.username.data, specialization=form.specialization.data, password=hashed_password, phone=form.phone.data, city=form.city.data)
        db.session.add(instructor)
        db.session.commit()
        flash('Your instructor account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register_instructor.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Assuming LoginForm is your form class
    if form.validate_on_submit():
        # Try to find the user in each role type
        user = Admin.query.filter_by(username=form.username.data).first() or \
               Instructor.query.filter_by(username=form.username.data).first() or \
               Client.query.filter_by(username=form.username.data).first()
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Set the role in the session for load_user to reference
            if isinstance(user, Admin):
                session['role'] = 'admin'
            elif isinstance(user, Instructor):
                session['role'] = 'instructor'
            elif isinstance(user, Client):
                session['role'] = 'client'
                
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html', form=form)






@app.route('/create_offering', methods=['GET', 'POST'])
@login_required
def create_offering():
    if not isinstance(current_user, Admin):  # Ensure only the admin can create offerings
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))

    form = OfferingForm()

    # Process form submission
    if form.validate_on_submit():
        # Create a new Offering object with a default offering_type and no instructor initially
        new_offering = Offering(
            lesson_type=form.lesson_type.data,
            location_id=form.location.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            maximum_capacity=form.maximum_capacity.data,
            offering_type=form.offering_type.data or "General"  # Default if not specified
            # instructor_id remains None for later assignment
        )
        
        # Add the new offering to the database
        db.session.add(new_offering)
        db.session.commit()

        # Add the offering to OfferingsCatalog
        OfferingsCatalog.offerings.append(new_offering)

        flash('Offering created successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('create_offering.html', form=form)





@app.route('/create_location', methods=['GET', 'POST'])
@login_required
def create_location():
    # Check if the current user is an admin based on class
    if not current_user.is_authenticated or current_user.__class__.__name__ != 'Admin':
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('index'))

    form = LocationForm()
    if form.validate_on_submit():
        # Create a new location
        location = Location(city=form.city.data, address=form.address.data, name=form.name.data)
        db.session.add(location)
        db.session.commit()
        flash("Location created successfully!", "success")
        return redirect(url_for('index'))

    return render_template('create_location.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
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
    if offering.is_assigned:
        flash('This offering has already been claimed.', 'warning')
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
    # Ensure the user is a client
    if not isinstance(current_user, Client):
        flash('Only clients can attend offerings.', 'danger')
        return redirect(url_for('index'))
    
    # Fetch the offering
    offering = Offering.query.get_or_404(offering_id)
    
    # Check if there are available spots and if the client is not already an attendee
    if offering.available_spots > 0:
        if current_user not in offering.attendees:
            # Add client to attendees and decrement available spots
            offering.attendees.append(current_user)
            offering.available_spots -= 1  # Decrement available spots
            db.session.commit()
            flash('You are now attending this offering!', 'success')
        else:
            flash('You are already attending this offering.', 'info')
    else:
        flash('Sorry, no available spots left for this offering.', 'danger')
    
    return redirect(url_for('index'))


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
    
    # Remove attendee and increment available spots
    if attendee in offering.attendees:
        offering.attendees.remove(attendee)
        offering.available_spots += 1
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
    
    # Delete user based on type
    if user_type == 'client':
        user = Client.query.get_or_404(user_id)
    elif user_type == 'instructor':
        user = Instructor.query.get_or_404(user_id)
    else:
        flash('Invalid user type specified.', 'danger')
        return redirect(url_for('manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash(f'{user_type.capitalize()} account deleted successfully!', 'success')
    return redirect(url_for('manage_users'))





if __name__ == "__main__":
    app.run(debug=True)

