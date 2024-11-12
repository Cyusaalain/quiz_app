from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager
from models import User, Module, Assessment, Question
from flask_wtf import CSRFProtect
from flask import session

# Initialize the Flask app and configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_app.db'
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
csrf = CSRFProtect(app)

# Define a simple route to test
@app.route('/')
def home():
    return render_template('home.html')

# Load user function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Admin login route
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

# User login route
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

# User registration route
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

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Admin dashboard
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    
    # Fetch all modules to display
    modules = Module.query.all()
    return render_template('admin_dashboard.html', modules=modules)

# Create new module route (Admin only)
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

# Deleting a module (Admin only)
@app.route('/delete_module/<int:module_id>', methods=['POST'])
@login_required
def delete_module(module_id):
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    
    module = Module.query.get_or_404(module_id)
    db.session.delete(module)
    db.session.commit()
    
    flash('Module deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

#  Module Dashboard with all assessments for a specific module
@app.route('/module_dashboard/<int:module_id>', methods=['GET'])
@login_required
def module_dashboard(module_id):
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    
    module = Module.query.get_or_404(module_id)
    assessments = Assessment.query.filter_by(module_id=module.id).all()
    return render_template('module_dashboard.html', module=module, assessments=assessments)

# creating a new assessment
@app.route('/module/<int:module_id>/create_assessment', methods=['GET', 'POST'])
@login_required
def create_assessment(module_id):
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    
    module = Module.query.get_or_404(module_id)
    assessment = None  # Initialize as None for GET requests
    
    if request.method == 'POST':
        # Extract data from the form
        title = request.form.get('title')
        terms = request.form.get('terms')
        time_limit = request.form.get('time_limit')

        # Create a new assessment and commit it to the database
        new_assessment = Assessment(title=title, terms=terms, time_limit=int(time_limit), module=module)
        db.session.add(new_assessment)
        db.session.commit()

        assessment = new_assessment  # Pass the new assessment to the template
        
        flash('Assessment created successfully! You can now add questions.', 'success')
        # Redirect to the question addition page after the assessment is created
        return redirect(url_for('add_questions', assessment_id=assessment.id))

    return render_template('create_assessment.html', module=module, assessment=assessment)

# editing an assessment
@app.route('/edit_assessment/<int:assessment_id>', methods=['GET', 'POST'])
@login_required
def edit_assessment(assessment_id):
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    
    assessment = Assessment.query.get_or_404(assessment_id)
    module = assessment.module  # Fetch the related module
    
    if request.method == 'POST':
        # Update assessment fields here
        assessment.title = request.form.get('title')
        assessment.terms = request.form.get('terms')
        assessment.time_limit = request.form.get('time_limit')
        
        db.session.commit()
        return redirect(url_for('module_dashboard', module_id=module.id))
    
    return render_template('edit_assessment.html', assessment=assessment, module=module)

#  deleting an assessment
@app.route('/delete_assessment/<int:assessment_id>', methods=['POST'])
@login_required
def delete_assessment(assessment_id):
    if current_user.role != 'admin':
        return redirect(url_for('home'))

    assessment = Assessment.query.get_or_404(assessment_id)
    
    Question.query.filter_by(assessment_id=assessment_id).delete()
    
    db.session.delete(assessment)
    db.session.commit()
    
    flash('Assessment and related questions deleted successfully!', 'success')
    return redirect(url_for('module_dashboard'))

#questions route
@app.route('/assessment/<int:assessment_id>/add_questions', methods=['GET', 'POST'])
@login_required
def add_questions(assessment_id):
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    
    assessment = Assessment.query.get_or_404(assessment_id)
    
    if request.method == 'POST':
        # Gather form data
        question_text = request.form.get('question_text')
        answer_options = request.form.getlist('answer_options')
        correct_answer = request.form.get('correct_answer')
        
        # Basic validation
        if not question_text or not answer_options or not correct_answer:
            flash('Please fill in all fields.', 'danger')
            return redirect(url_for('add_questions', assessment_id=assessment_id))
        
        # Store question details in session as a dictionary
        new_question = {
            'question_text': question_text,
            'answer_options': answer_options,
            'correct_answer': correct_answer
        }
        
        # Add the question to the session
        if 'questions' not in session:
            session['questions'] = []
        
        session['questions'].append(new_question)
        session['question_count'] = len(session['questions'])
        
        # Check which button was pressed
        if 'add_another' in request.form:
            flash('Question added. You can add another question.', 'info')
            return redirect(url_for('add_questions', assessment_id=assessment_id))
        
        if 'submit_final' in request.form:
            # Save all questions from the session to the database
            for question in session['questions']:
                new_question = Question(
                    question_text=question['question_text'],
                    answer_options=question['answer_options'],
                    correct_answer=question['correct_answer'],
                    assessment=assessment
                )
                db.session.add(new_question)
            
            db.session.commit()
            
            # Clear the session
            session.pop('questions', None)
            session.pop('question_count', None)
            
            flash('Quiz added successfully!', 'success')
            return redirect(url_for('module_dashboard', module_id=assessment.module_id))
    
    return render_template('add_questions.html', assessment=assessment)

#edit questions
@app.route('/edit_previous_question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_previous_question(question_id):
    if 'questions' not in session or question_id >= len(session['questions']):
        flash('No previous question to edit or invalid question ID.', 'error')
        return redirect(url_for('add_questions', assessment_id=assessment.id))
    
    question = session['questions'][question_id]

    if request.method == 'POST':
        question['question_text'] = request.form.get('question_text')
        question['answer_options'] = request.form.getlist('answer_options')
        question['correct_answer'] = request.form.get('correct_answer')
        session['questions'][question_id] = question
        flash('Question updated successfully.', 'success')
        return redirect(url_for('add_questions', assessment_id=question['assessment_id']))

    return render_template('edit_question.html', question=question, question_id=question_id)

# User dashboard
@app.route('/user_dashboard')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        return redirect(url_for('home'))
    return "Welcome to the User Dashboard!"

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)
