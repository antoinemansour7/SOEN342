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
    return Client.query.get(int(user_id))

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
    form = LoginForm()
    # (additional login logic here)
    return render_template('login.html', form=form)




if __name__ == "__main__":
    app.run(debug=True)

