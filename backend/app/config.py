import os
import dotenv
dotenv.load_dotenv()
class Config:
    CSRF_ENABLED = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///quiz_master.db'
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False