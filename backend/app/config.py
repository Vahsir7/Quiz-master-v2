import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    CSRF_ENABLED = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///quiz_master.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

