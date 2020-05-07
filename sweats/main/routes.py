from flask import render_template, Blueprint
from sweats.orders.forms import OrderItemForm
from sweats.carts.forms import CartItemForm
from sweats.models import Item
from flask_mail import Message


# Initializing Blueprint
main = Blueprint('main', '__name__')

@main.route("/")
@main.route("/home")
def home():
    items = Item.query.all()
    order_form = OrderItemForm()
    cart_form = CartItemForm()
    return render_template('home.html', items=items, order_form=order_form, cart_form=cart_form)

@main.route('/about')
def about():
    return render_template('about.html', title='About')