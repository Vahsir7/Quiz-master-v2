import os

from flask import Flask
from .config import Config
from flask_cors import CORS
from dotenv import load_dotenv

def create_app(config_class=Config):
    """Create and configure an instance of the Flask application."""
    load_dotenv()  
    #print("SECRET_KEY from .env:", os.getenv('SECRET_KEY')) 
    from .extension import db, bcrypt, migrate
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    
    from .controllers.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    from .controllers.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    from .controllers.student import student_bp
    app.register_blueprint(student_bp, url_prefix='/api/student')

    with app.app_context():
        from . import models
        db.create_all()
        admin = models.Admin.query.get(1)
        if not admin:
            #print("Creating admin user...")
            admin = models.Admin(
                AdminID=1,
                Name=os.getenv('Admin_Username'),
                Email=os.getenv('Admin_Email'),
            )
            password = os.getenv('Admin_Password')
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            #print("Admin created successfully.")
        #else:
            #print("Admin already exists.")

    return app

