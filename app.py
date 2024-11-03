from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from models import db, Client, Instructor, Offering, Child
from forms import LoginForm, ClientRegistrationForm, InstructorRegistrationForm
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
migrate = Migrate(app, db)

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    # Attempt to load the user as a Client first
    user = Client.query.get(int(user_id))
    if not user:
        # If not found as Client, attempt to load as Instructor
        user = Instructor.query.get(int(user_id))
    return user

# Main route for index
@app.route('/')
def index():
    offerings = Offering.query.all()
    return render_template('index.html', offerings=offerings)

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
        # Attempt to find user in both Client and Instructor models
        user = Client.query.filter_by(username=form.username.data).first()
        if not user:
            user = Instructor.query.filter_by(username=form.username.data).first()
        
        # Check password and log in if valid
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f"Welcome back, {user.username}!", 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))




if __name__ == "__main__":
    app.run(debug=True)

