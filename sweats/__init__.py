from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from sweats.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

# The user is redirected to login if unauthorized to access any route 
login_manager.login_view = 'customers.login'
login_manager.login_message_category = 'info'

mail = Mail()


# Moving the creation of 'app' object into a function. So that, 
# We can then create multiple instances of this app later for different purposes.
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from sweats.admin.routes import admin
    from sweats.carts.routes import carts
    from sweats.customers.routes import customers
    from sweats.main.routes import main
    from sweats.orders.routes import orders
    from sweats.errors.handlers import errors

    app.register_blueprint(admin)
    app.register_blueprint(carts)
    app.register_blueprint(customers)
    app.register_blueprint(main)
    app.register_blueprint(orders)
    app.register_blueprint(errors)

    return app
