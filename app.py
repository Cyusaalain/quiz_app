from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize the Flask app and configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_app.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong key

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# Define a simple route to test
@app.route('/')
def home():
    return "Welcome to the Quiz App!"

# Only run the server if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)