import os

class Config:
    # A 16 byte secret key
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # To hide warning
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Mail configuration
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    # os.environ.get() raises an exception if env not found os.getenv() returns None
    # Environment var. is set in .bashrc file ,     
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')