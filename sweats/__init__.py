from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Setting Up Development DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'
app.config['SQLALCHEMY_ECHO'] = True

# Create DB Instance 
db = SQLAlchemy(app)

items = [
    {
        'category':'Cloths',
        'description':'Wool cloths for children.',
        'unit_price':1500,
        'image_file':'default.jpg'
    },
    {
        'category':'Mobile',
        'description':'Smartphones with blah blah specifications.',
        'unit_price':9999,
        'image_file':'default.jpg'
    },
    {
        'category':'Watch',
        'description':'Water proof watches.',
        'unit_price':2600,
        'image_file':'default.jpg'
    },
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', items=items)

@app.route('/about')
def about():
    return render_template('about.html', title='About')

from sweats.models import Customer, Order, Item, Cart, Shipment, Warehouse