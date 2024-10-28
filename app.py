from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from extensions import db, login_manager 
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from flask import request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User  # Import User after db initialization to avoid circular import
from functools import wraps
from flask import abort

# Initialize the Flask app and configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_app.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong key

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)

# Define a simple route to test
@app.route('/')
def home():
    return "Welcome to the Quiz App!"

# Load user function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return abort(403)  # Forbidden access
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@admin_required
def admin_dashboard():
    return "Welcome to the Admin Dashboard!"

# register routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if the email is already registered
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists.')
            return redirect(url_for('register'))

        # Add new user to the database
        new_user = User(
            name=name, 
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Check email and password.')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Only run the server if this script is executed directly
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)