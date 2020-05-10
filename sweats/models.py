from datetime import datetime, timedelta
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin
from sweats import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(int(user_id))

def calShipDate():
    return datetime.utcnow() + timedelta(days=7)

# UserMixin adds certain fileds to our user such as is_authenticated, etc. see documents
class Customer(db.Model, UserMixin):
    __tablename__= 'customers'
    id = db.Column(db.Integer , primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    city = db.Column(db.String(20), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    orders = db.relationship('Order' , backref='owner' , lazy=True)
    cart_items = db.relationship('CartItem', backref='owner', lazy=True)

    # Token to get password reset
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        # Returns a token with given payload
        return s.dumps({'customer_id': self.id}).decode('utf-8')

    # Verify the token, token is ok, expires or valid?
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            # If the token is expires of invalid, then we get an error when accessing 'customer_id'
            # Return a dictionary
            customer_id = s.loads(token)['customer_id']
        except:
            return None
        return Customer.query.get(customer_id)

    def __repr__(self):
        return f"Customer('{self.id}', '{self.name}', '{self.admin}',  '{self.email}', '{self.image_file}', '{self.city}')"

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer , primary_key=True)
    order_date = db.Column(db.DateTime , default=datetime.utcnow)

    # sum of all amount of each individual OrderItem
    total_amount = db.Column(db.Integer , nullable=False)
    customer_id = db.Column(db.Integer , db.ForeignKey('customers.id') , nullable=False)
    order_items = db.relationship('OrderItem' , backref='order' , lazy=True)
    shipment = db.relationship('Shipment' , backref='order' , lazy=True)

    def __repr__(self):
        return f"Order('{self.id}', '{self.order_date}', '{self.total_amount}' , '{self.customer_id}')"

class OrderItem(db.Model):
    __tablename__ = 'orderitems'
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), primary_key=True)
    item_id = db.Column(db.Integer , db.ForeignKey('items.id') , primary_key=True)
    quantity = db.Column(db.Integer , nullable=False)

    def __repr__(self):
        return f"Order-Item('{self.order_id}', '{self.item_id}', '{self.quantity}')"

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer , primary_key=True)
    category = db.Column(db.String(20))
    description = db.Column(db.String(200), nullable=False)
    image_file = db.Column(db.String(20), nullable=False)
    unit_price = db.Column(db.Integer , nullable=False)

    # Item-OrderItem : One-Many
    order_items = db.relationship('OrderItem' , backref='item' , lazy=True)

    def __repr__(self):
        return f"Item('{self.id}', '{self.category}', '{self.description}', '{self.image_file}', '{self.unit_price}')"


class Shipment(db.Model):
    __tablename__ = 'shipments'
    order_id = db.Column(db.Integer , db.ForeignKey('orders.id') , primary_key=True)
    warehouse_id = db.Column(db.Integer , db.ForeignKey('warehouses.id') , primary_key=True)

    # Shipment is done inbetween 7 days from Order
    ship_date = db.Column(db.DateTime ,default=calShipDate, nullable=False)

    def __repr__(self):
        return f"Shipment('{self.order_id}', '{self.warehouse_id}', '{self.ship_date}')"

class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50), unique=True, nullable=False)

    # Warehouse-Shipment : One-Many
    shipments = db.relationship('Shipment' , backref='warehouse' , lazy=True)

    def __repr__(self):
        return f"Warehouse('{self.id}', '{self.city}')"

class CartItem(db.Model):
    __tablename__= 'cartitems'
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Cart('{self.customer_id}', '{self.item_id}', '{self.quantity}')"