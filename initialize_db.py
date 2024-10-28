from app import db, app
from models import User  # Import the User model to ensure it’s included in the database schema

# Use the app context to ensure db.create_all() has the correct context
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")