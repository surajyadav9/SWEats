import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)

# Setting Up Development DB
app.config['SECRET_KEY'] = '8882a369b09a45cce3fa1ea1b5ca425d'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

# Creating Instances
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

# The user redirected to login if unauthorized to access any route 
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# os.environ.get() raises an exception if env not found os.getenv() returns None
# Environment var. is set in .bashrc file , 
# use $ source ~/.bashrc to make env. var. exist
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
mail = Mail(app)


from sweats.routes import customer_routes
from sweats.routes import admin_routes