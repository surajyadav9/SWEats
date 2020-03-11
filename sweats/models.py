from datetime import datetime
from sweats import db

class Customer(db.Model):
    __tablename__= 'customers'
    id = db.Column(db.Integer , primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(20), nullable=False)
    
    # 'owner' is the owner of an order
    # customer-order : one-many
    orders = db.relationship('Order' , backref='owner' , lazy=True)

    def __repr__(self):
        return f"Customer('{self.id}', '{self.name}', '{self.city}')"

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer , primary_key=True)
    order_date = db.Column(db.DateTime , default=datetime.utcnow)
    customer_id = db.Column(db.Integer , db.ForeignKey('customers.id') , nullable=False)
    order_amount = db.Column(db.Integer , nullable=False)

    # Order-OrderItem : One-Many
    orderitems = db.relationship('OrderItem' , backref='order' , lazy=True)

    # order-shipment : one-many
    shipments = db.relationship('Shipment' , backref='order' , lazy=True)

    def __repr__(self):
        return f"Order('{self.id}', '{self.order_date}', '{self.customer_id}' , '{self.order_amount}')"

class OrderItem(db.Model):
    __tablename__ = 'orderitems'
    order_id = db.Column(db.Integer , db.ForeignKey('orders.id') , primary_key=True)
    item_id = db.Column(db.Integer , db.ForeignKey('items.id') , primary_key=True)
    quantity = db.Column(db.Integer , nullable=False)

    def __repr__(self):
        return f"Order-Item('{self.order_id}', '{self.item_id}', '{self.quantity}')"

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer , primary_key=True)
    unit_price = db.Column(db.Integer , nullable=False)

    # Item-OrderItem : One-Many
    orderitems = db.relationship('OrderItem' , backref='item' , lazy=True)

    def __repr__(self):
        return f"Item('{self.id}', '{self.unit_price}')"


class Shipment(db.Model):
    __tablename__ = 'shipments'
    order_id = db.Column(db.Integer , db.ForeignKey('orders.id') , primary_key=True)
    warehouse_id = db.Column(db.Integer , db.ForeignKey('warehouses.id') , primary_key=True)
    ship_date = db.Column(db.DateTime , default = datetime.utcnow , nullable=False)

    def __repr__(self):
        return f"Shipment('{self.order_id}', '{self.warehouse_id}', '{self.ship_date}')"

class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50), nullable=False)

    # Warehouse-Shipment : One-Many
    shipments = db.relationship('Shipment' , backref='warehouse' , lazy=True)

    def __repr__(self):
        return f"Warehouse('{self.id}', '{self.city}')"