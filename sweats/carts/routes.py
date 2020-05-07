from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from sweats import db
from sweats.carts.forms import CartItemForm
from sweats.models import Item, Warehouse, Order, OrderItem, Shipment, CartItem


# Initializing Blueprint
carts = Blueprint('carts', '__name__')


@carts.route('/item/<int:item_id>/cart', methods=['POST'])
@login_required
def add_to_cart(item_id):
    form = CartItemForm()
    if form.validate_on_submit():
        # Check wether the item already exist in cart
        cart_item = CartItem.query.filter_by(customer_id=current_user.id, item_id=item_id).first()
        if cart_item:
            flash("This item already exist in your cart!", 'info')
        else:
            cart_item = CartItem(customer_id=current_user.id, item_id=item_id, quantity=form.quantity.data)
            db.session.add(cart_item)
            db.session.commit()
            flash("Item added to your cart!", 'success')
    else:
        flash("Maximum 4 quantity can be added to cart!", 'danger')
    return redirect(url_for('main.home'))

@carts.route("/cart")
@login_required
def cart():
    cartList = CartItem.query.filter_by(customer_id=current_user.id).order_by()
    cartItems = {}
    for cart in cartList:
        item = Item.query.get_or_404(cart.item_id)
        cartItems[item] = cart.quantity
    return render_template('cart.html', items=cartItems)

@carts.route('/cart/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_cart_item(item_id):
    cart_item = CartItem.query.filter_by(customer_id=current_user.id, item_id=item_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash("Successfully removed item from cart!", 'success')
        return redirect(url_for('carts.cart'))
    else:
        # Bad request
        abort(400)

@carts.route('/cart/buy', methods=['POST'])
@login_required
def buy_cart():
    cart = CartItem.query.filter_by(customer_id=current_user.id).first()
    if not cart:
        flash("Cart is empty!", 'info')
        return redirect(url_for('main.home'))

    warehouse = Warehouse.query.filter_by(city=current_user.city).first()
    if not warehouse:
        flash('Your city is not reachable to us! Sorry for inconvenience.', 'info')
        return redirect(url_for('main.home'))

    cart = CartItem.query.filter_by(customer_id=current_user.id)
    total_amount=0
    for cart_item in cart:
        item = Item.query.get_or_404(cart_item.item_id)
        total_amount += (item.unit_price * cart_item.quantity)

    # Add order to DB
    order = Order(customer_id=current_user.id, total_amount=total_amount)
    db.session.add(order)
    db.session.commit()

    # Add Shipment to DB
    shipment = Shipment(order_id=order.id, warehouse_id=warehouse.id, warehouse=warehouse, order=order)
    db.session.add(shipment)
    db.session.commit()

    # Add OrderItems
    for cart_item in cart:
        order_item = OrderItem(order_id=order.id, item_id=cart_item.item_id, quantity=cart_item.quantity)
        db.session.add(order_item)
        db.session.delete(cart_item)
    db.session.commit()
    return redirect(url_for('orders.customer_orders'))