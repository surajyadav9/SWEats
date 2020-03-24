from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

# Setting Up Development DB
app.config['SECRET_KEY'] = '8882a369b09a45cce3fa1ea1b5ca425d'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

# Create DB Instance 
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

# The user redirected to login if unauthorized to access any route 
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from sweats import routes