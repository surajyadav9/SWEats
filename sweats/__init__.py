from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Setting Up Development DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'
app.config['SQLALCHEMY_ECHO'] = True

# Create DB Instance 
db = SQLAlchemy(app)

from sweats.models import Customer, Order, Item, OrderItem, Shipment, Warehouse