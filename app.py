from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from models import db, User, Offering  # Correct import of db
from forms import LoginForm, RegistrationForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

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
    offerings = Offering.query.all()
    return render_template('index.html', offerings=offerings)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
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
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Additional route for selecting offerings
@app.route('/select_offering/<int:offering_id>')
@login_required
def select_offering(offering_id):
    if current_user.role == 'instructor':
        offering = Offering.query.get(offering_id)
        if offering and offering.is_available:
            offering.is_available = False
            offering.instructor_id = current_user.id
            db.session.commit()
            flash('You have successfully selected the offering!', 'success')
        else:
            flash('Offering is not available.', 'danger')
    else:
        flash('Only instructors can select offerings.', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Bind the app context to ensure that db commands are executed within the app context
    with app.app_context():
        db.create_all()  # Ensures that the database and tables are created if they don't exist
    app.run(debug=True)




