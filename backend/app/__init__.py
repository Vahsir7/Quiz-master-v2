from flask import Flask
import os
from .config import Config
from flask_cors import CORS

def create_app(config_class=Config):
    from .extension import db, bcrypt, migrate, mail, celery, cache
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    
    celery.conf.update(
        broker_url=Config.broker_url,
        result_backend=Config.result_backend
    )
    celery.conf.beat_schedule = Config.CELERY_BEAT_SCHEDULE
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask

    # Register blueprints
    from .controllers.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    from .controllers.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    from .controllers.student import student_bp
    app.register_blueprint(student_bp, url_prefix='/api/student')

    @app.cli.command("init-db")
    def init_db_command():
        """Creates the database tables and initial admin."""
        from . import models
        db.create_all()
        admin = models.Admin.query.get(1)
        if not admin:
            admin = models.Admin(
                AdminID=1,
                Name=os.getenv('Admin_Username'),
                Email=os.getenv('Admin_Email'),
            )
            password = os.getenv('Admin_Password')
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
        print("Initialized the database.")

    return app