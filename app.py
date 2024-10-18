from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from models import db, User, Offering  # Correct import of db
from forms import LoginForm, RegistrationForm, OfferingForm
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
migrate = Migrate(app, db)

# Initialize db with app
db.init_app(app)


bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    offerings = Offering.query.all()  # Fetch all offerings from the database
    return render_template('index.html', offerings=offerings)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        # Look up the user by username
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Log the user in
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    offerings = Offering.query.all()
    return render_template('dashboard.html', offerings=offerings)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, age=form.age.data, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)



@app.route('/create-offering', methods=['GET', 'POST'])
@login_required
def create_offering():
    form = OfferingForm()
    
    if current_user.role != 'admin':
        flash('Only admins can create offerings!')
        return redirect(url_for('index'))
    
    if form.validate_on_submit():
        # Check if it's a group lesson and set maximum capacity
        if form.lesson_type.data == 'Group' and form.maximum_capacity.data is None:
            flash('Please provide maximum capacity for group lessons.')
            return render_template('create_offering.html', form=form)
        
        # Create the offering
        new_offering = Offering(
            lesson_type=form.lesson_type.data,
            mode=form.mode.data,
            location=form.location.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            maximum_capacity=form.maximum_capacity.data if form.lesson_type.data == 'Group' else None,
            is_available=form.is_available.data
        )
        
        # Add the new offering to the database
        db.session.add(new_offering)
        db.session.commit()
        
        flash('New offering created successfully!')
        return redirect(url_for('index'))
    
    return render_template('create_offering.html', form=form)


@app.route('/attend_offering/<int:offering_id>', methods=['POST'])
@login_required
def attend_offering(offering_id):
    offering = Offering.query.get_or_404(offering_id)
    
    if offering.lesson_type == 'group' and len(offering.attendees) >= offering.maximum_capacity:
        flash('This group lesson is full!', 'danger')
        return redirect(url_for('index'))
    
    # Check if the user is already attending this offering
    if current_user in offering.attendees:
        flash('You are already attending this offering.', 'info')
    else:
        offering.attendees.append(current_user)
        db.session.commit()
        flash('You are now attending this offering!', 'success')
    
    return redirect(url_for('index'))




if __name__ == "__main__":
    app.run(debug=True)

