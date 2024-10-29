from app import db, app
from models import User, Module, Assessment, Question

# Use the app context to ensure db.create_all() has the correct context
with app.app_context():
    db.metadata.clear()  
    db.drop_all()       
    db.create_all()      
    print("Database tables created successfully!")