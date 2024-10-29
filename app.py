from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from extensions import db, login_manager 
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Module, Assessment, Question
from functools import wraps
from flask import abort

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default="user")

class Module(db.Model):
    __tablename__ = 'modules'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    assessments = db.relationship('Assessment', backref='module', lazy=True)

class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    terms = db.Column(db.Text, nullable=True)
    time_limit = db.Column(db.Integer)  # Time limit in minutes
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    questions = db.relationship('Question', backref='assessment', lazy=True)

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    answer_options = db.Column(db.JSON)  # JSON field for multiple-choice options
    correct_answer = db.Column(db.String(100), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)

# Initialize the Flask app and configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_app.db'
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)

# Define a simple route to test
@app.route('/')
def home():
    return render_template('home.html')

# Load user function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email, role='admin').first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.')
    return render_template('admin_login.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email, role='user').first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid user credentials.')
    return render_template('user_login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email address already exists.')
            return redirect(url_for('register'))

        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.')
        return redirect(url_for('user_login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

#admin dashboard
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    
    # Fetch all modules to display
    modules = Module.query.all()
    return render_template('admin_dashboard.html', modules=modules)

@app.route('/create_module', methods=['GET', 'POST'])
@login_required
def create_module():
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        new_module = Module(title=title, description=description)
        db.session.add(new_module)
        db.session.commit()
        
        return redirect(url_for('admin_dashboard'))
    
    return render_template('create_module.html')

@app.route('/module/<int:module_id>/create_assessment', methods=['GET', 'POST'])
@login_required
def create_assessment(module_id):
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    
    module = Module.query.get_or_404(module_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        terms = request.form.get('terms')
        time_limit = request.form.get('time_limit')
        
        new_assessment = Assessment(title=title, terms=terms, time_limit=int(time_limit), module=module)
        db.session.add(new_assessment)
        db.session.commit()
        
        return redirect(url_for('admin_dashboard'))
    
    return render_template('create_assessment.html', module=module)

#user dashboard
@app.route('/user_dashboard')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        return redirect(url_for('home'))
    return "Welcome to the User Dashboard!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)