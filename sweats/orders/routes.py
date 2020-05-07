from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import current_user, login_required
from sweats import db
from sweats.orders.forms import OrderItemForm
from sweats.carts.forms import CartItemForm
from sweats.models import Item, Warehouse, Order, OrderItem, Shipment


# Initializing Blueprint
orders = Blueprint('orders', '__name__')

@orders.route('/item/<int:item_id>/order', methods=['POST'])
@login_required
def place_order(item_id):
    form = OrderItemForm()
    if form.validate_on_submit():
        warehouse = Warehouse.query.filter_by(city=current_user.city).first()
        if not warehouse:
            flash('Your city is not reachable to us! Sorry for inconvenience.', 'info')
            return redirect(url_for('main.home'))

        unit_price = Item.query.get_or_404(item_id).unit_price
        order_amount = unit_price * form.quantity.data

        # Adding Order to database
        order = Order(total_amount=order_amount, customer_id=current_user.id, owner=current_user)
        db.session.add(order)
        db.session.commit()

        # Adding OrderItem to DB
        order_item = OrderItem(order_id=order.id, item_id=item_id, quantity=form.quantity.data, order=order)
        db.session.add(order_item)
        db.session.commit()

        # Adding Shipment to DB
        shipment = Shipment(order_id=order.id, warehouse_id=warehouse.id, warehouse=warehouse, order=order)
        db.session.add(shipment)
        db.session.commit()
        flash('Your order processed successfully!', 'success')
    else:
        flash("Maximum 4 quantity can be ordered at a time!", 'danger')
    return redirect(url_for('main.home'))

@orders.route("/orders")
@login_required
def customer_orders():
    # Paginating orders
    # (argument_name, default-vlue, type)
    page = request.args.get('page', 1, type=int)

    orderList = Order.query.filter_by(customer_id=current_user.id).order_by(Order.order_date.desc()).paginate(page=page, per_page=1)
    orderItems = {}
    for order in orderList.items:
        items = []
        for orderItem in order.order_items:
            item = Item.query.get_or_404(orderItem.item_id)
            pair = (item, orderItem.quantity)
            items.append(pair)
        orderItems[order] = items
    return render_template('orders.html', title="Orders", orders=orderList, orderItems=orderItems)