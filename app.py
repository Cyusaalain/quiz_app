from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_app.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong key

db = SQLAlchemy(app)
login_manager = LoginManager(app)

@app.route('/')
def home():
    return "Welcome to the Quiz App!"

if __name__ == '__main__':
    app.run(debug=True)