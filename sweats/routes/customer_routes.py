import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from sweats import app, db, bcrypt
from sweats.forms import RegistrationForm, LoginForm, UpdateAccountForm, ItemForm, UpdateItemForm, OrderItemForm, CartItemForm
from sweats.models import Customer, Item, Warehouse, Order, OrderItem, Shipment, CartItem

@app.route("/")
@app.route("/home")
def home():
    items = Item.query.all()
    order_form = OrderItemForm()
    cart_form = CartItemForm()
    return render_template('home.html', items=items, order_form=order_form, cart_form=cart_form)

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        pw_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        customer = Customer(name=form.name.data, email=form.email.data, password=pw_hash, city=form.city.data)
        db.session.add(customer)
        db.session.commit()

        # here 'success' is a bootstrap class for flash messages
        flash('Account created successfully. Now you can log in.', 'success')
        # again 'home' is the function name
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        customer = Customer.query.filter_by(email=form.email.data).first()
        if customer and bcrypt.check_password_hash(customer.password, form.password.data):
            login_user(customer, remember=form.remember.data)
            
            # The page user attempting to access w/o authorization will be passed in the next query string variable
            # Here get return 'None' if query string variable 'next' is not found in the args dictionary
            next_page = request.args.get('next')

            # Python Ternary operation
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password!', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture, folder, size_x, size_y):
    # Giving each picture to its own unique id
    random_hex = secrets.token_hex(8)
    _ , f_ext = os.path.splitext( form_picture.filename )
    picture_filename = random_hex + f_ext

    # app.root_path = /home/suraj/Desktop/SWEats/sweats
    picture_path = os.path.join( app.root_path, folder, picture_filename )
    
    # Resizing the profile picture
    output_size = (size_x, size_y)
    im = Image.open(form_picture)
    im.thumbnail(output_size)
    im.save(picture_path)

    return picture_filename

def delete_old_picture(picture_filename, folder):
    picture_path = os.path.join( app.root_path, 'static/'+folder, picture_filename )
    os.remove(picture_path)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            # Delete old pictures
            if current_user.image_file != 'default.png':
                delete_old_picture(current_user.image_file, 'profile_pics')

            picture_file = save_picture(form.picture.data, "static/profile_pics", 125, 125)
            current_user.image_file = picture_file
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.city = form.city.data
        db.session.commit()
        flash('Account updated successfully!', 'success')

        # After submiting a form, if we reload a page w/o redirecting, the browser tries to send a POST request again(i.e tries to submit the form again)
        # redirect causes the browser to send a GET request( POST/REDIRECT/GET Pattern )
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.city.data = current_user.city
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route('/item/<int:item_id>/order', methods=['POST'])
@login_required
def place_order(item_id):
    form = OrderItemForm()
    if form.validate_on_submit():
        warehouse = Warehouse.query.filter_by(city=current_user.city).first()
        if not warehouse:
            flash('Your city is not reachable to us! Sorry for inconvenience.', 'info')
            return redirect(url_for('home'))

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
    return redirect(url_for('home'))

@app.route("/orders")
@login_required
def orders():
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

@app.route('/item/<int:item_id>/cart', methods=['POST'])
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
    return redirect(url_for('home'))

@app.route("/cart")
@login_required
def cart():
    cartList = CartItem.query.filter_by(customer_id=current_user.id).order_by()
    cartItems = {}
    for cart in cartList:
        item = Item.query.get_or_404(cart.item_id)
        cartItems[item] = cart.quantity
    return render_template('cart.html', items=cartItems)

@app.route('/cart/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_cart_item(item_id):
    cart_item = CartItem.query.filter_by(customer_id=current_user.id, item_id=item_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash("Successfully removed item from cart!", 'success')
        return redirect(url_for('cart'))
    else:
        # Bad request
        abort(400)

@app.route('/cart/buy', methods=['POST'])
@login_required
def buy_cart():
    cart = CartItem.query.filter_by(customer_id=current_user.id).first()
    if not cart:
        flash("Cart is empty!", 'info')
        return redirect(url_for('home'))

    warehouse = Warehouse.query.filter_by(city=current_user.city).first()
    if not warehouse:
        flash('Your city is not reachable to us! Sorry for inconvenience.', 'info')
        return redirect(url_for('home'))

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
    return redirect(url_for('orders'))