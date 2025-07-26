import os
from flask import Flask
from .config import Config
from flask_cors import CORS

def create_app(config_class=Config):
    from .extension import db, bcrypt, migrate, mail, celery
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    
    # Update celery config
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND'],
    )
    celery.conf.beat_schedule = {
        'send-daily-reminders': {
            'task': 'app.celery_tasks.send_daily_reminders',
            'schedule': timedelta(days=1),
        },
    }

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

    with app.app_context():
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

    return app