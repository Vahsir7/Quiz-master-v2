from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_mail import Mail
from celery import Celery

migrate = Migrate()
db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
celery = Celery()