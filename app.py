from flask import Flask, render_template, redirect, url_for, flash, request
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
    # Check if user is Client, Instructor, or Admin
    user = Client.query.get(int(user_id)) or Instructor.query.get(int(user_id)) or Admin.query.get(int(user_id))
    return user


@app.route('/')
def index():
    assigned_offerings = Offering.query.filter_by(is_assigned=True).all()
    unassigned_offerings = []

    if current_user.is_authenticated and (isinstance(current_user, Admin) or isinstance(current_user, Instructor)):
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
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        client = Client(username=form.username.data, name=form.name.data, phone=form.phone.data, password=hashed_password, age=form.age.data)
        db.session.add(client)
        db.session.commit()

        # If add_child checkbox is selected, create a Child instance
        if form.add_child.data:
            child = Child(name=form.child_name.data, age=form.child_age.data, relation=form.child_relation.data, guardian_id=client.id)
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
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        # Check Client, Instructor, and Admin for the user
        user = (Client.query.filter_by(username=form.username.data).first() or
                Instructor.query.filter_by(username=form.username.data).first() or
                Admin.query.filter_by(username=form.username.data).first())

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f"Welcome back, {user.username}!", 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')

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




if __name__ == "__main__":
    app.run(debug=True)

