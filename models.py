# models.py
from extensions import db
from flask_login import UserMixin

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default="user")

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    assessments = db.relationship('Assessment', backref='module', lazy=True)

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    terms = db.Column(db.Text, nullable=True)
    time_limit = db.Column(db.Integer)  # Time limit in minutes
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    questions = db.relationship('Question', backref='assessment', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    answer_options = db.Column(db.JSON)  # JSON field for multiple-choice options
    correct_answer = db.Column(db.String(100), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)